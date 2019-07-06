#除了 data 参数和 timeout 参数外，还有 context 参数，它必须是 ssl.SSLContext 类型，用来指定
#SSL 设置 。
#此外， cafile 和 ca path 这两个参数分别指定 CA 证书和它的路径，这个在请求 HTTPS 链接时会
#有用 。
#cadefault 参数现在已经弃用了，其默认值为 False 。
#前面讲解了 ur lopen （）方法的用法，通过这个最基本的方法，我们可以完成简单的请求和网页抓
#取。 若需更加详细的信息，可以参见官方文档 ： https ://docs .python.or的／Ii brary/url Iib. request. html
