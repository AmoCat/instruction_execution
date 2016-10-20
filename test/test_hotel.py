# coding: utf-8
import requests
import json

#url = "http://127.0.0.1:9527/module/instruction_execution"
#url = "http://0.0.0.0:9527/module/instruction_execution/hotel"
url = "http://0.0.0.0:9527/module/instruction_execution/hotel"



content = '后天北京五道口的宾馆'
context = {'test':'test'}
ltp = {'seg': '后天 北京 五道口 的 宾馆',
        'pos': 'nt ns ns u n',
        'ner': 'O S-Ns S-Ns O O'}
metafield = {'ltp': ltp}
values = {'content': content, 'context':context, 'metafield': metafield}

response = requests.post(url, json = values)
print response.json()
