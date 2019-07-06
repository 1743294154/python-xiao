#timeout 参数用于设置超时时间，单位为秒，意思就是如果请求超 出 了设置的这个时间， 还没有得
#到响应 ， 就会抛出异常。 如果不指定该参数 ，就会使用全局默认时间 。 它支持 HTTP , HTTPS 、 FTP
#请求 。

#下面例子开看一下：
import urllib.request

response = urllib.request.urlopen('http://httpbin.org/get',timeout=1)
print(response.read())

#这里我们设置超时时间是 l 秒。 程序 l 秒过后，服务器依然没有响应，于是抛出了 U RL Error 异常 。
