#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : async_websocket.py
@Author     : LeeCQ
@Date-Time  : 2023/2/12 21:47
"""
import logging
import time

from websocket import WebSocket

logger = logging.getLogger(__name__)

ws = WebSocket()
ws.connect("ws://t.leecq.cn:29090/traffic?token=123456", timeout=5)

# WebSocketApp().run_forever()
while True:
    _ss = time.time()
    time.sleep(5)
    _r = ws.recv(), ws.recv(), ws.recv(), ws.recv(), ws.recv()
    print('recv: -----------------')
    print(time.time() - _ss, _r)
# Path: pyclash\monitor\async_websocket.py
