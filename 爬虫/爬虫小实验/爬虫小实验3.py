#爬虫网页，爬一个百度的网站，
import urllib.request
response=urllib.request.urlopen('https://www.baidu.com')
#前面两个输出响应的状态码和响应的头信息
print(response.status)
print(response.getheaders())
print(response.getheader('Server'))
#通过调用getheader（）方法并传递一个参数server获取了响应
#头中的Server值，结果是nginx，意思是服务器是用Nginx搭建的
#利用最基本的urlopen（）方法，可以完成最基本的简单网页的GET请求抓取。

#如果想给链接传递一些参数，该怎么实现呢？首先看一下urlopen（）函数的API:
#urllib.request.urlopen(url,data=None,[timeout,]*,cafile=None,capath=None,cadefault=False,context=None)
#可以发现，除了第一个参数可以传递URL之外，我们还可以传递其他内容，比如data（附加数据）、timeout（超时时间）等。

#data参数
#data参数是可选的，如果要添加该参数，并且如果它是字节流编码格式的内容，即bytes类型，则需要通过bytes（）方法转化。
#另外，如果传递了这个参数，则它的请求方式就不再是GET方式，而是POST方式了
import urllib.parse
import urllib.request

data = bytes(urllib.parse.urlencode({'word':'hello'}),encoding='utf8')
response = urllib.request.urlopen('http://httpbin.org/post',data=data)
print(response.read())

#这里我们传递了一个参数 word ，值是 hello o 它需要被转码成 bytes （字节流）类型 。 其中转字
#节流采用了 bytes （）方法，该方法的第一个参数需要是 str （字符串）类型，需要用 urllib.parse 模
#块里的 urlencode （）方法来将参数字典转化为字符串；第二个参数指定编码格式，这里指定为 utf8
#这里请求的站点是 httpbin.org，它可以提供 HTTP 请求测试。本次我们请求的 URL 为 http://httpbin.
#org/ post ，这个链接可以用来测试 POST 请求，它可以输出请求的一些信息 ，其中包含我们传递的 data
#参数。