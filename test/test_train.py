# coding: utf-8
import requests
import json

#url = "http://127.0.0.1:9527/module/instruction_execution"
url = "http://0.0.0.0:9527/module/instruction_execution/train"



content = '后天从北京到哈尔滨'
context = {'test':'test'}
ltp = {'seg': '后天 从 北京 到 哈尔滨',
        'pos': 'nt p ns p ns',
        'ner': 'O O S-Ns O S-Ns'}
metafield = {'ltp': ltp}
values = {'content': content, 'context':context, 'metafield': metafield}

response = requests.post(url, json = values)
print response.json()
