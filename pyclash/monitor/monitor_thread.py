#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : __init__.py.py
@Author     : LeeCQ
@Date-Time  : 2023/2/10 21:41
"""
import json
import logging
import os
import threading
import time
import urllib.parse
from collections import namedtuple
from queue import Queue, Empty
from threading import Thread as _Thread
from typing import List

import urllib3
import urllib3.exceptions
from websocket import WebSocketApp

logger = logging.getLogger('pyclash.monitor')


class Thread(_Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon, ):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.target = target
        self.args = args
        self.kwargs = kwargs


class Monitor:
    """Clash Monitor To Grafana Loki.  """

    _clash_info = namedtuple('clash_info', ['host', 'port', 'token', 'log_level'])
    _loki_info = namedtuple('loki_info', ['url', 'user', 'token'])

    def __init__(self, clash_info: List = None, loki_info: List = None, loki_push_class=None):

        self.clash_info = set()
        self.loki_info = set()
        self.loki_sessions = []
        self.received_size = 0

        for clash_host, clash_port, clash_token, log_level in clash_info or set():
            self.add_clash_info(clash_host, clash_port, clash_token, log_level)

        for loki_url, loki_user, loki_token in loki_info or set():
            self.add_loki_info(loki_url, loki_user, loki_token)

        self.threads = []
        self.log_queue = Queue()
        self.upload_queue = Queue()
        self.loki_push_class = (loki_push_class or PushToLokiSync)()

    def add_loki_info(self, loki_url, loki_user=None, loki_token=None):
        """add loki info        """

        self.loki_info.add(self._loki_info(loki_url, loki_user, loki_token))

    def exit(self):
        logger.debug('Wait For Queue `log_queue` to be empty, (current has %s), ',
                     self.log_queue.qsize())
        self.log_queue.join()
        time.sleep(1)
        logger.error('The Execution of the program is No Input, Will Exit ...')
        os._exit(1)

    def check_ws(self):
        """check ws"""
        while True:
            alive_size = 0
            for t in self.threads:
                if not t.is_alive():
                    self.threads.remove(t)
                    logger.warning('Thread %s is not alive, try reconnecting ...', t.name)
                    t_new = Thread(target=t.target, args=t.args, kwargs=t.kwargs, daemon=True, name=t.name)
                    t_new.start()
                    self.threads.append(t_new)
                else:
                    alive_size += 1
            logger.debug('Check Thread Alive, Current Threads Size: %s', alive_size)
            time.sleep(30)

    def add_clash_info(self, clash_host, clash_port, clash_token='', log_level='INFO'):
        """add clash info

        """
        self.clash_info.add(
            self._clash_info(clash_host, clash_port, clash_token, log_level)
        )

    def on_message(self, ws_client: WebSocketApp, message, ):
        """Websocket Message Callback.

        When on message, put message to log_queue.
        """
        logger.debug('From %s: %s', ws_client.url, message.replace('\n', ''))

        urlparse = urllib.parse.urlparse(ws_client.url)
        self.received_size += 1
        self.log_queue.put(
            {'timestamp': time.time_ns(),
             'name': urlparse.path.split('/')[-1],
             'host': urlparse.netloc,
             'from_url': ws_client.url,
             'message': message
             }, block=False)

    def ws_steam(self, uri, ):
        """start"""
        for clash_host, clash_port, clash_token, log_level in self.clash_info:
            _token = f'token={clash_token}' if clash_token else ''
            _level = f'level={log_level}' if log_level else ''
            ws_url = urllib.parse.urljoin(f'ws://{clash_host}:{clash_port}{uri}',
                                          f'?{_token}&{_level}')
            logger.info('Start Monitor %s, ', ws_url)

            ws_client = WebSocketApp(
                ws_url,
                on_message=self.on_message,
            )
            _ = Thread(target=ws_client.run_forever, daemon=True,
                       name=f'{clash_host}_{uri.split("/")[-1]}')
            _.start()
            self.threads.append(_)

    def ws_start(self):
        """start"""

        self.ws_steam('/traffic')
        self.ws_steam('/profile/tracing')
        # self.ws_steam('/logs')  # TODO:

        Thread(target=self.check_ws, daemon=True, name='check_ws').start()

    def parse_log(self, data: dict) -> dict:
        """parse log  """
        raise NotImplementedError

    def parse_traffic(self, data: dict) -> dict:
        """parse traffic """
        raise NotImplementedError

    def parse_tracing(self, data: dict) -> dict:
        """parse tracing """
        raise NotImplementedError

    def post_loki(self, data: dict):
        """post loki

        eg. https://github.com/sleleko/devops-kb/blob/master/python/push-to-loki.py
        """
        for loki_url, loki_user, loki_token in self.loki_info:
            logger.debug('put info to Class: %s', loki_url)
            self.loki_push_class.add_post_data(loki_url, loki_user, loki_token, data)

    def start_parse(self):
        case = {
            'logs': self.parse_log,
            'traffic': self.parse_traffic,
            'tracing': self.parse_tracing,
        }

        while True:
            if not self.log_queue.empty():
                data: dict = self.log_queue.get()
                # noinspection PyArgumentList
                _parse = case.get(data['name'], lambda x: x)(data)
                logger.debug('生成结果：%s', _parse)
                self.post_loki(_parse)
                # self.log_queue.task_done()

    def run(self):
        """run"""

        self.ws_start()
        time.sleep(1)

        logger.info('Start Parse Thread ...')
        Thread(target=self.start_parse, daemon=True, name='parse').start()

        logger.info('Start Loki Push Thread ...')
        Thread(target=self.loki_push_class.run, daemon=True, name='loki_push').start()

        while True:
            time.sleep(60)
            logger.info('Received Size at last %s: total_received_size=%s, total_send_size=%s, '
                        'push_request_size=%s, request_error_size=%s, queue_size=%s send_queue_size=%s',
                        time.strftime('%x %X'),
                        self.received_size,
                        self.loki_push_class.total_push_size,
                        self.loki_push_class.total_push_size,
                        self.loki_push_class.error_count,
                        self.log_queue.qsize(),
                        {urllib.parse.urlparse(k.url).netloc: v.qsize()
                         for k, v in self.loki_push_class.sync_queue.items()},
                        )


class MonitorV1(Monitor):
    """Clash Monitor To Grafana Loki.    """

    def __init__(self, clash_info: List = None, loki_info: List = None, ):
        """init"""
        super().__init__(clash_info, loki_info)

    def parse_log(self, data: dict) -> dict:
        """parse log """
        logger.debug('parse log: %s', data['message'])
        return {
            "stream": {
                "job": "clash",
                "type": "log",
                "host": data['host'],
            },
            "values": [
                [str(data['timestamp']), data['message']]
            ]
        }

    def parse_traffic(self, data: dict) -> dict:
        """parse traffic"""
        logger.debug('parse log: %s', data['message'])

        message = json.loads(data['message'])
        message['type'] = data['name']
        return {
            "stream": {
                "job": "clash",
                "type": "traffic",
                "host": data['host'],
            },
            "values": [
                [str(data['timestamp']), json.dumps(message)]
            ]
        }

    def parse_tracing(self, data: dict) -> dict:
        """parse tracing """
        logger.debug('parse log: %s', data['message'])

        message = json.loads(data['message'])
        if message.get('metadata'):
            message['metadata_dstip'] = message['metadata']['destinationIP']
            message['metadata_dstport'] = message['metadata']['destinationPort']
            message['metadata_host'] = message['metadata']['host']
            message['metadata_network'] = message['metadata']['network']
            message['metadata_srcip'] = message['metadata']['sourceIP']
            message['metadata_srcport'] = message['metadata']['sourcePort']
            message['metadata_type'] = message['metadata']['type']
            message['metadata_dnsmode'] = message['metadata']['dnsMode']
            del message['metadata']

        return {
            "stream": {
                "job": "clash",
                "type": message['type'].lower(),
                "host": data['host'],
            },
            "values": [
                [str(data['timestamp']),
                 json.dumps(message, sort_keys=False, ensure_ascii=False)]
            ]
        }


class PushToLokiSync:
    """Push To Loki"""
    _post_data = namedtuple('PostData', ['url', 'username', 'password'])

    def __init__(self, max_workers=10, user=None, password=None, headers: dict = None):
        from requests import Session
        from concurrent.futures import ThreadPoolExecutor

        self.session = Session()

        self.session.verify = False
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        if user and password:
            self.session.auth = user, password
        if headers:
            self.session.headers.update(headers)

        self.executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix='PushToLokiSync'
        )
        self.sync_queue = dict()

        self.total_request_size = 0
        self.total_push_size = 0
        self.error_count = 0

    def run(self):
        """run"""
        logger.info('start PushToLokiSync in Thread: %s', threading.current_thread().name)
        while True:
            time.sleep(1)
            if not self.sync_queue:
                logger.debug('Sync Queue is Empty. Will Sleep 1s')
                continue

            for key in self.sync_queue.keys():
                data_s = self.pop_data(key)
                if not data_s:
                    continue

                logger.debug('submit a task: %s, data size %s', key.url, len(data_s))
                # Commit a Task to ThreadPoolExecutor
                self.executor.submit(
                    self.post,
                    key.url,
                    key.username,
                    key.password,
                    data_s
                )

    def add_post_data(self, url: str, user=None, password=None, data: dict = ''):
        """add post data"""
        key = self._post_data(url, user, password)

        if key not in self.sync_queue:
            self.sync_queue[key] = Queue()

        logger.debug('put data to Queue: %s, data: %s', key, data)
        self.sync_queue.get(key).put(data)

    def pop_data(self, key, lens=100):
        """pop data"""
        lens = lens - 1
        _data = []
        try:
            for _ in range(lens):
                _data.append(self.sync_queue.get(key, []).get(timeout=1))
        except Empty:
            logger.debug('Queue not have %s lens, return %s lens: ',
                         lens, len(_data))
        return _data

    def post(self, url, user, password, streams: list):
        """post"""
        logger.debug('Post to Loki: %s, data: %s', url, len(streams))
        try:
            _res = self.session.post(
                url,
                json={"streams": streams},
                auth=None if user is None else (user, password),
                timeout=10,
                verify=False
            )
        except Exception as _e:
            logger.exception('Loki Post Error, %s', _e)
            for _ in streams:
                self.add_post_data(url, user, password, _)
            return
        logger.debug('Loki Response: %s, (HttpCode %s)', _res.text, _res.status_code)

        if _res.status_code != 204:
            self.error_count += 1
            logger.error('Loki Push Error: %s (http_code: %s)', _res.text, _res.status_code)
            for _ in streams:
                self.add_post_data(url, user, password, _)
        else:
            self.total_request_size += 1
            self.total_push_size += len(streams)


if __name__ == '__main__':
    logging.basicConfig(

        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(lineno)s - %(threadName)s - [%(levelname)s] %(message)s')
    a = MonitorV1()
    a.add_clash_info('192.168.0.4', 29090, '123456', 'DEBUG')
    a.add_clash_info('t.leecq.cn', 29090, '123456', 'DEBUG')
    a.add_loki_info('https://logs-prod-017.grafana.net/loki/api/v1/push', '345975',
                    'eyJrIjoiZWMxMDIwODNiMGNmZTg3MmU3OWFlZmZlMzUyNjcxODllYWZjY'
                    'jkyZSIsIm4iOiJweXRlc3QiLCJpZCI6NzYxNTc0fQ==')
    a.add_loki_info('http://192.168.0.4:3100/loki/api/v1/push', )
    # a.ws_start()

    a.run()
