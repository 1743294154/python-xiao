#我们知道利用 urlopen （）方法可以实现最基本请求的发起，但这几个简单的参数并不足以构建一
#个完整的请求 。 如果请求中需要加入 Headers 等信息，就可以利用更强大的 Request 类来构建。
#首先，我们用实例来感受一下 Request 的用法：
import urllib .request
request = urllib.request.Request(' https://www.baidu.com')
response = urllib .request.urlopen(request)
print(response.read().decode('utf-8'))