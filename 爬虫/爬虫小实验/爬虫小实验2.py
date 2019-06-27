#抓一个python官网的网页
import urllib.request
response = urllib.request.urlopen('https://www.python.org')
#print(response.read().decode('utf-8'))
print(type(response))#利用type（）方法输出响应的类型。