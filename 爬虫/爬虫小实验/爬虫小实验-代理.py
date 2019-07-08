#代理
#在做爬虫的时候，免不了要使用代理，如果要添加代理，可以这样做：
from urllib.error import URLError
from urllib.request import ProxyHandler,build_opener
proxy_handler = ProxyHandler({
'http':' http://127.o.o .1:9743 ',
'https':'https://127.0 .0.1:9743 '
})
opener = build_opener(proxy_handler)
try:
    response = opener.open('https://www.baidu.com')
    print(response.read() .decode('utf-8'))
except URLError as e:
    print(e .reason)
#这里我们在本地搭建了一个代理，它运行在 9743 端口上 。
#这里使用了 ProxyHand ler ，其参数是一个字典，键名是协议类型（比如 HTTP 或者 HTTPS 等），
#键值是代理链接，可以添加多个代理.
#然后，利用这个 Handler 及 build_opener（）方法构造一个 Opener ，之后发送请求即可