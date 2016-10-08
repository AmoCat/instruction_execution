# coding: utf-8
import requests
import json

#url = "http://127.0.0.1:9527/module/instruction_execution"
url = "http://0.0.0.0:9527/module/instruction_execution/flight"



content = '我想飞美国'
context = {'test':'test'}
ltp = {'seg': '我 想 飞 美国',
        'pos': 'r v v ns',
        'ner': 'O O O S-Ns'}
metafield = {'ltp': ltp}
values = {'content': content, 'context':context, 'metafield': metafield}

response = requests.post(url, json = values)
print response.json()
