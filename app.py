#coding:utf-8

from flask import Flask, render_template, jsonify, request
from language_understanding import TrainCommander,FlightCommander,HotelCommander,BusCommander
import json
import traceback
import re

app = Flask('benben-lu')
app.config.from_object('config')

from flask.ext.bootstrap import Bootstrap
Bootstrap(app)

STATUS_SUCCESS = 0
STATUS_WAITING = 1
STATUS_INTERUPT = 2

MSG_TYPE_TEXT = 'text'
MSG_TYPE_TICKET = 'tickets'

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/module/instruction_execution/train', methods=['POST'])
def get_train_reply():
    commander = TrainCommander()
    res = reply(commander)
    return res

@app.route('/module/instruction_execution/flight', methods=['POST'])
def get_flight_reply():
    commander = FlightCommander()
    res = reply(commander)
    return res

@app.route('/module/instruction_execution/hotel', methods=['POST'])
def get_hotel_reply():
    commander = HotelCommander()
    res = reply(commander)
    return res

@app.route('/module/instruction_execution/bus', methods=['POST'])
def get_bus_reply():
    commander = BusCommander()
    res = reply(commander)
    return res

def reply(commander):
    app.logger.info(request.json)
    sent = request.json.get('content')
    context = request.json.get('context')
    metafield = request.json.get('metafield')

    app.logger.info('INPUT: ' + '\t'.join([sent, str(context)]))
    try:
        if metafield and 'ltp' in metafield.keys():
            ltp = metafield.get('ltp')
            seg = ltp.get('seg').split()
            pos = ltp.get('pos').split()
            nes = ltp.get('ner').split()
            status, reply, context = commander.get_reply_with_lexical(sent, seg, pos, nes, context)
        else:
            status, reply, context = commander.get_reply(sent, context)
    except Exception as e:
        traceback.print_exc()
        app.logger.info(str(e))
        status = STATUS_INTERUPT
        reply = ''
        context = {}
    app.logger.info('OUTPUT: ' + '\t'.join([str(status), reply, str(context)]))
    msg_type = MSG_TYPE_TEXT
    if status == STATUS_SUCCESS:
            not_find = re.search("没有找到",reply)
            before_date = re.search("昨天",reply)
            unsupported_city = re.search("不支持的",reply)
            error = re.search("有误",reply)
            if not (not_find or before_date or unsupported_city or error):
                msg_type = MSG_TYPE_TICKET
    return jsonify({'msg_type': msg_type,'status': status, 'reply': reply, 'context': context, 'metafield':{}})