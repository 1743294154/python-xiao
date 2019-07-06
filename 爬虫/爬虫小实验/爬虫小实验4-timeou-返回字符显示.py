#该异常属于 urllib. error 模块，错误原因是超时。
#因此 ，可以通过设置这个超时时间来控制一个网页如果长时间未响应，就跳过它的抓取 。 这可以
#利用 try except 语句来实现 ，相关代码如下：
import socket
import urllib.request
import urllib.error

try:
    response = urllib.request.urlopen('http://httpbin.org/get',timeout=0.1)
except urllib.error.URLError as e:
    if isinstance(e.reason,socket.timeout):
        print('TIME OUT')
#这里我们请求了 h即：／/h忧pbin.org/get 测试链接，设置超时时间是 O l 秒，然后捕获了 URL Error 异
#常，接着判断异常是 socket.timeout 类型（意思就是超时异常），从而得出它确实是因为超时而报错 ，
#打印输出了 TIME OUT。