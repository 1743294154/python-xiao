# coding=utf-8

import argparse
from pathlib import Path
from pap_logger import __example_name__, _pap_logger_example

parser = argparse.ArgumentParser(description=__example_name__,
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-v", "--verbose_fmt", help="Verbose formatting.", action="store_true")
parser.add_argument("-p", "--log_path", help="Path to log directory.", type=Path,
                    default=Path("/tmp") / __example_name__)
parser.add_argument("-sh", "--syslog_host", help="Syslog hostname.", type=str)

args = parser.parse_args()
_pap_logger_example(verbose_fmt=args.verbose_fmt, syslog_host=args.syslog_host, log_path=args.log_path)
