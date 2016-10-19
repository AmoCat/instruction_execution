# coding: utf-8
import requests
import json

#url = "http://127.0.0.1:9527/module/instruction_execution"
url = "http://0.0.0.0:9527/module/instruction_execution/hotel"



content = '后天从北京到哈尔滨'
context = {'test':'test'}
ltp = {'seg': '后天 北京 的 宾馆',
        'pos': 'nt ns u n',
        'ner': 'O S-Ns O O'}
metafield = {'ltp': ltp}
values = {'content': content, 'context':context, 'metafield': metafield}

response = requests.post(url, json = values)
print response.json()
