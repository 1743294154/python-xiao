import requests
ret = requests.get('https://github.com/timeline.json')
print
var = ret.url
print
ret.text()