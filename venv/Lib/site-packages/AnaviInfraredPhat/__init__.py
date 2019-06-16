#!/usr/bin/env python3
# coding=utf-8
"""
ANAVI Infrared pHAT
"""

import json
import logging
import time

import pigpio

PIGPIO_PORT = 8888

BH1750_I2CADDR = 0x23
BMP180_I2CADDR = 0x77
HTU21D_I2C_ADDR = 0x40

BMP180_ULTRALOWPOWER = 0
BMP180_STANDARD = 1
BMP180_HIGHRES = 2
BMP180_ULTRAHIGHRES = 3


class AnaviInfraredPhatException(BaseException):
    """
    BaseException for this module
    """

    def __init__(self, msg):
        super().__init__()
        logging.exception(msg)


class AnaviInfraredPhat:
    """
    Super class for I2C sensors.
    """

    def __init__(self, pi, bus=1, address=0x00):
        """
      Instantiate with the Pi.
      The default I2C bus is 1 and a 0x00 address for this parent class.
      """
        self.pi = pi
        try:
            self.h = self.pi.i2c_open(bus, address)
        except Exception:
            raise AnaviInfraredPhatException("Could not obtain a handle")

    def _write_registers(self, data):
        try:
            self.pi.i2c_write_device(self.h, data)
        except Exception as _:
            self.cancel()
            raise AnaviInfraredPhatException("Could not write to registers")

    def _read_registers(self, reg, count):
        try:
            return self.pi.i2c_read_i2c_block_data(self.h, reg, count)
        except Exception as e:
            self.cancel()
            logging.exception(e)
            return None

    def cancel(self):
        """
      Cancels the sensor and releases resources.
      """
        if self.h is not None:
            self.pi.i2c_close(self.h)
            self.h = None


class BH1750(AnaviInfraredPhat):
    """
   A class to read the BH1750 light sensor.
   """
    _LUXDELAY = 0.5

    def __init__(self, pi, bus=1, address=BH1750_I2CADDR):
        super().__init__(pi, bus, address)

    def get_lux(self):
        """
        :return:returns luminosity from BH1750 sensor (in lux)
        """
        try:
            self._write_registers([0x10])
            time.sleep(self._LUXDELAY)
            c, d = self._read_registers(0x00, 2)
            return int.from_bytes(d, byteorder='big', signed=True)
        except Exception:
            raise AnaviInfraredPhatException("Could not obtain luminosity")


class HTU21D(AnaviInfraredPhat):
    """
   A class to read the HTU21D light sensor.
   """
    _TEMP = 0xF3
    _HUMID = 0xF5
    _HTU21D_DELAY = 0.1

    def __init__(self, pi, bus=1, address=HTU21D_I2C_ADDR):
        super().__init__(pi, bus, address)

    def get_temperature(self):
        """
        :return: returns temperature from HTU21D sensor.
        """
        try:
            self._write_registers([self._TEMP])
            time.sleep(self._HTU21D_DELAY)
            c, rt = self.pi.i2c_read_device(self.h, 2)
            temp = int.from_bytes(rt, byteorder='big', signed=False) / 65536.0
            return -46.85 + (175.72 * temp)
        except Exception:
            raise AnaviInfraredPhatException("Could not get temperature from HTU21D")

    def get_humidity(self):
        """
        :return: returns humidity from HTU21D sensor.
        """
        try:
            self._write_registers([self._HUMID])
            time.sleep(self._HTU21D_DELAY)
            c, rh = self.pi.i2c_read_device(self.h, 2)
            humid = int.from_bytes(rh, byteorder='big', signed=False) / 65536.0
            return -6.0 + (125.0 * humid)
        except Exception:
            raise AnaviInfraredPhatException("Coild not get humidity from HTU21D")


class BMP180(AnaviInfraredPhat):
    """
   A class to read the BMP180 pressure and temperature sensor.
   """

    _calib00 = 0xD0
    _CAL_AC1 = 0xAA
    _CAL_AC2 = 0xAC
    _CAL_AC3 = 0xAE
    _CAL_AC4 = 0xB0
    _CAL_AC5 = 0xB2
    _CAL_AC6 = 0xB4
    _CAL_B1 = 0xB6
    _CAL_B2 = 0xB8
    _CAL_MB = 0xBA
    _CAL_MC = 0xBC
    _CAL_MD = 0xBE
    _CONTROL = 0xF4
    _TEMPDATA = 0xF6
    _PRESSUREDATA = 0xF6
    _READTEMPCMD = 0x2E
    _READPRESSURECMD = 0x34

    _pressure_delay_ms = [5, 8, 14, 26]

    def __init__(self, pi, sampling=BMP180_ULTRAHIGHRES, bus=1, address=BMP180_I2CADDR):
        """
      Instantiate with the Pi.
      Optionally the over sampling rate may be set (default 1).
      For I2C the default bus is 1 and default address is 0x77.
      Example using I2C, bus 1, address 0x77
      s = BMP180(pi)
      """
        try:
            super().__init__(pi, bus, address)
        except Exception:
            raise AnaviInfraredPhatException("Could not init BMP180")

        self.sampling = sampling
        try:
            self._load_calibration()
        except Exception:
            raise AnaviInfraredPhatException("Could not calibrate BMP180")

        self.measure_temperature_delay = (5 / 1000.0)
        self.measure_pressure_delay = (BMP180._pressure_delay_ms[self.sampling] / 1000.0)
        self.t_fine = 0.0

    def _load_calibration(self):

        c, d1 = self._read_registers(BMP180._calib00, 8)
        if d1 == 0x55:
            raise AnaviInfraredPhatException("Fail to calibrate BMP180")

        # Read calibration data
        c, d1 = self._read_registers(BMP180._CAL_AC1, 2)
        self.ac1 = int.from_bytes(d1, byteorder='big', signed=True)
        c, d1 = self._read_registers(BMP180._CAL_AC2, 2)
        self.ac2 = int.from_bytes(d1, byteorder='big', signed=True)
        c, d1 = self._read_registers(BMP180._CAL_AC3, 2)
        self.ac3 = int.from_bytes(d1, byteorder='big', signed=True)
        c, d1 = self._read_registers(BMP180._CAL_AC4, 2)
        self.ac4 = int.from_bytes(d1, byteorder='big', signed=False)
        c, d1 = self._read_registers(BMP180._CAL_AC5, 2)
        self.ac5 = int.from_bytes(d1, byteorder='big', signed=False)
        c, d1 = self._read_registers(BMP180._CAL_AC6, 2)
        self.ac6 = int.from_bytes(d1, byteorder='big', signed=False)

        c, d1 = self._read_registers(BMP180._CAL_B1, 2)
        self.b1 = int.from_bytes(d1, byteorder='big', signed=True)
        c, d1 = self._read_registers(BMP180._CAL_B2, 2)
        self.b2 = int.from_bytes(d1, byteorder='big', signed=True)

        c, d1 = self._read_registers(BMP180._CAL_MB, 2)
        self.mb = int.from_bytes(d1, byteorder='big', signed=True)
        c, d1 = self._read_registers(BMP180._CAL_MC, 2)
        self.mc = int.from_bytes(d1, byteorder='big', signed=True)
        c, d1 = self._read_registers(BMP180._CAL_MD, 2)
        self.md = int.from_bytes(d1, byteorder='big', signed=True)

    def _read_raw_temp(self):
        self._write_registers([BMP180._CONTROL, BMP180._READTEMPCMD])
        time.sleep(self.measure_temperature_delay)
        c, d = self._read_registers(BMP180._TEMPDATA, 2)
        rt = int.from_bytes(d, byteorder='big', signed=True)
        return rt

    def _compute_b5(self, rt):
        x1 = ((rt - self.ac6) * self.ac5) >> 15
        x2 = (self.mc << 11) / (x1 + self.md)
        # if x1:
        #  x2 = (self.mc << 11)/(x1 + self.md)
        # else:
        #  x2=0
        return int(x1 + x2)

    def get_temperature(self):
        """
        :return: temperature from the BMP180 sensor.
        """
        try:
            ut = self._read_raw_temp()
            compensate = self._compute_b5(ut)
            raw_temperature = ((compensate + 8) >> 4)
            return raw_temperature / 10
        except Exception:
            raise AnaviInfraredPhatException("Could not get temperature from BMP180")

    def _read_raw_pressure(self):
        self._write_registers([BMP180._CONTROL, BMP180._READPRESSURECMD + (self.sampling << 6)])
        time.sleep(self.measure_pressure_delay)
        c, d = self._read_registers(BMP180._PRESSUREDATA, 2)
        rp = int.from_bytes(d, byteorder='big', signed=False)
        rp <<= 8
        c, d = self._read_registers(BMP180._PRESSUREDATA + 2, 2)
        rp |= int.from_bytes(d, byteorder='big', signed=False)
        rp >>= (8 - self.sampling)
        return rp

    def get_pressure(self):
        """
        :return: atmospheric pressure from the BMP180 sensor.
        """
        try:
            ut = self._read_raw_temp()
            up = self._read_raw_pressure()
            b6 = self._compute_b5(ut) - 4000
            x1 = (self.b2 * ((b6 * b6) >> 12)) >> 11
            x2 = (self.ac2 * b6) >> 11
            x3 = x1 + x2
            b3 = (((self.ac1 * 4 + x3) << self.sampling) + 2) / 4
            x1 = (self.ac3 * b6) >> 13
            x2 = (self.b1 * ((b6 * b6) >> 12)) >> 16
            x3 = ((x1 + x2) + 2) >> 2
            b4 = (self.ac4 * (x3 + 32768)) >> 15
            b7 = (up - b3) * (50000 >> self.sampling)
            if b7 < 0x80000000:
                p = (b7 * 2) / b4
            else:
                p = (b7 / b4) * 2

            p = int(p)
            x1 = (p >> 8) * (p >> 8)
            x1 = (x1 * 3038) >> 16
            x2 = (-7357 * p) >> 16
            p += (x1 + x2 + 3791) >> 4
            return p / 100
        except Exception:
            raise AnaviInfraredPhatException("Could not get pressure from BMP180")


class IRSEND(AnaviInfraredPhat):
    """
   A class to send IR codes, adapted from Joan's script @ http://abyz.co.uk/rpi/pigpio/code/irrp_py.zip.
   Records file is to be created with this script
   """

    def __init__(self, pi, records_file, txgpio=17, txfreq=38.0, gap=100):
        super().__init__(pi)
        self.GPIO = txgpio
        self.FREQ = txfreq
        self.GAP_S = gap / 1000.0
        self.records_file = records_file
        self.code = []
        self.code2 = []
        self.h = None

    def carrier(self, micros):
        """
      Generate carrier square wave.
        :param micros:
        :return:
      """
        wf = []
        cycle = 1000.0 / self.FREQ
        cycles = int(round(micros / cycle))
        on = int(round(cycle / 2.0))
        so_far = 0
        for c in range(cycles):
            target = int(round((c + 1) * cycle))
            so_far += on
            off = target - so_far
            so_far += off
            wf.append(pigpio.pulse(1 << self.GPIO, 0, on))
            wf.append(pigpio.pulse(0, 1 << self.GPIO, off))
        return wf

    def send_ir(self, command):
        """
        :param command: command to pass to the air conditionner. Needs to match a key in the config file.
        :return:
        """
        try:
            f = open(self.records_file)
        except FileNotFoundError:
            return "Can't open: {}".format(self.records_file)
        records = json.load(f)
        f.close()
        self.pi.set_mode(self.GPIO, pigpio.OUTPUT)  # IR TX connected to this GPIO.
        self.pi.wave_add_new()
        emit_time = time.time()
        if command in records:
            self.code = records[command]
            # Create wave
            marks_wid = {}
            spaces_wid = {}
            wave = [0] * len(self.code)
            for i in range(0, len(self.code)):
                ci = self.code[i]
                if i & 1:  # Space
                    if ci not in spaces_wid:
                        self.pi.wave_add_generic([pigpio.pulse(0, 0, ci)])
                        spaces_wid[ci] = self.pi.wave_create()
                    wave[i] = spaces_wid[ci]
                else:  # Mark
                    if ci not in marks_wid:
                        wf = self.carrier(ci)
                        self.pi.wave_add_generic(wf)
                        marks_wid[ci] = self.pi.wave_create()
                    wave[i] = marks_wid[ci]
            delay = emit_time - time.time()
            if delay > 0.0:
                time.sleep(delay)
            self.pi.wave_chain(wave)
            while self.pi.wave_tx_busy():
                time.sleep(0.002)
            for i in marks_wid:
                self.pi.wave_delete(marks_wid[i])
            for i in spaces_wid:
                self.pi.wave_delete(spaces_wid[i])
            return "Command {} sent".format(command)
        else:
            return "Command {} not found".format(command)


def hvac(host, irfile, msg):
    """
    Sends an IR command to an air conditionner or a fan.
    :param host: host sending the command
    :param irfile: json configuration file containing a dictionnary of commands in pigpio format.
    :param msg: command to send (key to the dictionnary stored in the file)
    :return: result of the command
    """
    irtx = None

    pi = pigpio.pi(host, PIGPIO_PORT)
    if not pi.connected:
        raise AnaviInfraredPhatException("Could not connect to pigpiod on %s:%s" % (host, PIGPIO_PORT))

    try:
        irtx = IRSEND(pi, irfile)
        rtn = irtx.send_ir(msg)
        if irtx is not None:
            irtx.cancel()
            irtx = None
        pi.stop()
        return rtn
    except KeyboardInterrupt:
        if irtx is not None:
            irtx.cancel()
        return "User interrupted"
    except Exception:
        if irtx is not None:
            irtx.cancel()
        raise AnaviInfraredPhatException("Generic exception")


def report_tphl(host):
    """
    Reports temperature, atmospheric pressure, humidity level and luminosity from host's sensors.
    :param host: the host where the measures are made
    :return: dictionnary containing raw measures from each sensor if available, n/a otherwise.
    """
    rtn = {"bmp180": {"t": -4242.42, "p": -4242.42}, "htu21d": {"t": -4242.42, "h": -4242.42}, "bh1750": {"l": -4242}}
    bmp180 = None
    bh1750 = None
    htu21d = None
    exc = None
    try:
        pi = pigpio.pi(host, PIGPIO_PORT)
    except Exception:
        raise AnaviInfraredPhatException("Could not connect to pigpiod on %s:%s" % (host, PIGPIO_PORT))

    if not pi.connected:
        raise AnaviInfraredPhatException("Could not connect to pigpiod on %s:%s" % (host, PIGPIO_PORT))

    try:
        try:
            bmp180 = BMP180(pi)
            rtn["bmp180"]["t"] = bmp180.get_temperature()
            rtn["bmp180"]["p"] = bmp180.get_pressure()
        except AnaviInfraredPhatException:
            pass

        try:
            htu21d = HTU21D(pi)
            rtn["htu21d"]["t"] = htu21d.get_temperature()
            rtn["htu21d"]["h"] = htu21d.get_humidity()
        except AnaviInfraredPhatException:
            pass

        try:
            bh1750 = BH1750(pi)
            rtn["bh1750"]["l"] = bh1750.get_lux()
        except AnaviInfraredPhatException:
            pass

        return rtn
    except KeyboardInterrupt:
        exc = KeyboardInterrupt("User interrupted")
    except ConnectionAbortedError:
        exc = AnaviInfraredPhatException("Connection aborted error ({})".format(host))
    except pigpio.error:
        exc = AnaviInfraredPhatException("Pigpio error ({})".format(host))
    except Exception:
        exc = AnaviInfraredPhatException("Other Exception ({})".format(host))
    finally:
        if bmp180 is not None:
            bmp180.cancel()
        if bh1750 is not None:
            bh1750.cancel()
        if htu21d is not None:
            htu21d.cancel()
        if pi:
            pi.stop()
        if exc:
            raise exc


def _get_heat_index(temp: float, rh: float):
    """
    See https://en.wikipedia.org/wiki/Heat_index#Formula
    the formula uses fahrenheit, so we convert for computation and return back in celsuis
    :param temp:
    :param rh:
    :return:
    """
    if rh < 1:
        logging.warning("RH values changed from %s to %s" % (rh, rh * 100))
        rh *= 100
    if temp < 27 or rh < 40:
        return None, "No concerns"
    temp = (temp * 9 / 5) + 32
    c1 = -42.379
    c2 = 2.04901523
    c3 = 10.14333127
    c4 = -0.22475541
    c5 = -6.83783e-3
    c6 = -5.481717e-2
    c7 = 1.22874e-3
    c8 = 8.5282e-4
    c9 = -1.99e-6

    hi = c1 + (c2 * temp) + (c3 * rh) + (c4 * temp * rh)
    hi += (c5 * temp * temp) + (c6 * rh * rh) + (c7 * temp * temp * rh)
    hi += (c8 * temp * rh * rh) + (c9 * temp * temp * rh * rh)

    if hi < 80:
        cmt = "No concerns"
    elif hi < 90:
        cmt = "Caution"
    elif hi < 105:
        cmt = "Extreme Caution"
    elif hi < 130:
        cmt = "Danger"
    else:
        cmt = "Extreme Danger"
    hi = ((hi - 32) * 5) / 9

    return hi, cmt


def report_tphl_average(host):
    """
    Reports formatted temperature, atmospheric pressure, humidity level and luminosity
    :param host: the host where the measures are made
    :return: formatted string
    """
    values = report_tphl(host)
    if isinstance(values, str):
        # Error
        return {"t": -4242, "p": -4242, "h": -4242, "l": -4242, "hi": "", "hi_cmt": ""}
    else:
        avg_temp = round((values["bmp180"]["t"] + values["htu21d"]["t"]) / 2, 1)
        hi, hi_cmt = _get_heat_index(temp=avg_temp, rh=int(values["htu21d"]["h"]))
        return {"t": avg_temp,
                "p": int(values["bmp180"]["p"]),
                "h": int(values["htu21d"]["h"]),
                "l": int(values["bh1750"]["l"]),
                "hi": hi,
                "hi_cmt": hi_cmt
                }


def report_tphl_as_text(host):
    """
    Reports formatted temperature, atmospheric pressure, humidity level and luminosity
    :param host: the host where the measures are made
    :return: formatted string
    """
    values = report_tphl(host)
    if isinstance(values, str):
        # Error
        rtn = values
    else:
        avg_temp = round((values["bmp180"]["t"] + values["htu21d"]["t"]) / 2, 1)
        hi, hi_cmt = _get_heat_index(temp=avg_temp, rh=int(values["htu21d"]["h"]))
        rtn = "{}:\n".format(host)
        rtn += "\tTemperature\t{:.1f} C ({:.1f} / {:.1f})\n".format((values["bmp180"]["t"] + values["htu21d"]["t"]) / 2,
                                                                    values["bmp180"]["t"], values["htu21d"]["t"])
        rtn += "\tPressure\t\t{:d} hPa\n".format(int(values["bmp180"]["p"]))
        rtn += "\tHumidity\t\t{:d} %rh\n".format(int(values["htu21d"]["h"]))
        rtn += "\tLuminosity\t\t{:d} Lux".format(int(values["bh1750"]["l"]))
        rtn += "\tHeat Index\t\t{:d} : {}".format(hi, hi_cmt)
        rtn += "\n"
    return rtn


if __name__ == "__main__":
    print(report_tphl_as_text("localhost"))
