#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : __init__.py.py
@Author     : LeeCQ
@Date-Time  : 2023/2/10 21:41
"""
import logging
import time
import json
import urllib.parse
from queue import Queue
from threading import Thread

import requests
from websocket import WebSocketApp

logger = logging.getLogger('pyclash.monitor')


def push_to_loki(loki_url, data):
    """push to loki

    eg. https://github.com/sleleko/devops-kb/blob/master/python/push-to-loki.py
    """
    headers = {'Content-Type': 'application/json'}
    payload = {}
    requests.post(loki_url, json=payload, headers=headers)


class Monitor:
    """Clash Monitor To Grafana Loki."""

    def __init__(self, clash_host, clash_port=9090, token=None,
                 log_level='INFO'
                 ):
        """init"""
        self.clash_host = clash_host
        self.clash_port = clash_port
        self.clash_token = token
        self.log_level = log_level

        self.threads = []
        self.log_queue = Queue()

    def on_message(self, ws_client: WebSocketApp, message):
        """Websocket Message Callback.

        When on message, put message to log_queue.
        """
        logger.info('From %s: %s', ws_client.url, message.replace('\n', ''))

        self.log_queue.put(
            {'timestamp': int(time.time() * 1000 ** 2),
             'name': urllib.parse.urlparse(ws_client.url).path.split('/')[-1],
             'from_url': ws_client.url,
             'message': message
             }, block=False)

    def ws_steam(self, uri, args: dict = None):
        """start"""
        ws_url = f'ws://{self.clash_host}:{self.clash_port}{uri}?'
        ws_query = '&'.join([f'{k}={v}' for k, v in args.items()])
        args.pop('token', None)
        logger.info('Start Monitor %s, query=%s', ws_url, args)

        ws_client = WebSocketApp(
            ws_url + ws_query,
            on_message=self.on_message,
        )
        _ = Thread(target=ws_client.run_forever, daemon=True, name='connect_logs')
        _.start()
        self.threads.append(_)

    def ws_start(self):
        """start"""

        self.ws_steam('/traffic', args={'token': self.clash_token})
        self.ws_steam('/profile/tracing', args={'token': self.clash_token})
        self.ws_steam('/logs', args={'token': self.clash_token, 'level': self.log_level})

    def parse_log(self, data: dict):
        """parse log

        """
        log = json.loads(data.pop('message', ''))
        return log

    def parse_traffic(self, data: dict):
        """parse traffic

        """
        traffic = json.loads(data.pop('message', ''))
        return traffic

    def prase_tracing(self, data: dict):
        """parse tracing

        """
        profile = json.loads(data.pop('message', ''))
        return profile

    def run(self):
        """run"""
        case = {
            'logs': self.parse_log,
            'traffic': self.parse_traffic,
            'profile': self.prase_tracing,
        }

        while True:
            if not self.log_queue.empty():
                data = self.log_queue.get()
                _push = data['name'](data)
                logger.info(_push)
            time.sleep(1)


if __name__ == '__main__':
    a = Monitor(clash_host='127.0.0.1', clash_port=59429, token='1d235c4d-9586-42b3-a4a8-9716f2d44cf6', log_level='DEBUG')
    a.ws_start()

    while True:
        if not a.log_queue.empty():
            print(a.log_queue.get())
        time.sleep(1)
