#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : async_websocket.py
@Author     : LeeCQ
@Date-Time  : 2023/2/12 21:47
"""
import asyncio
import logging
import time
import urllib.parse
from collections import defaultdict, namedtuple

import websockets

from pyclash.monitor.data_parse import parse_logs, parse_traffic, parse_tracing

logger = logging.getLogger('pyclash.monitor.async_websocket')


async def websocket_app(uri: str, on_message: asyncio.Queue):
    """"""
    urlparse = urllib.parse.urlparse(uri)
    name = urlparse.path.split('/')[-1]

    async for websocket in websockets.connect(uri, close_timeout=1, open_timeout=1):
        try:
            while True:
                await on_message.put(
                    {'timestamp': time.time_ns(),
                     'name': name,
                     'host': urlparse.netloc,
                     'from_url': uri,
                     'message': await websocket.recv()
                     })
        except websockets.ConnectionClosed:
            logger.warning(f'websocket {uri} closed, reconnecting...')
            await asyncio.sleep(5)
            continue


class MonitorAsync:
    _clash_info = namedtuple('clash_info', ['host', 'port', 'token', 'log_level'])
    _loki_info = namedtuple('loki_info', ['url', 'user', 'token'])
    _post_data = namedtuple('PostData', ['url', 'username', 'password'])

    def __init__(self):

        self.clash_info = set()
        self.loki_info = set()

        self.clash_events = {'/profile/tracing', '/traffic', '/logs', }  # /events

    def add_loki(self, loki_url: str, loki_username: str, loki_password: str):
        """add loki info"""
        self.loki_info.add(self._loki_info(loki_url, loki_username, loki_password))

    def add_clash_info(self, clash_host, clash_port, clash_token='', log_level='INFO'):
        """add clash info"""
        self.clash_info.add(self._clash_info(clash_host, clash_port, clash_token, log_level))

    def add_websocket_tasks(self):
        """添加WebSocket任务"""
        for clash in self.clash_info:
            for event in self.clash_events:
                asyncio.create_task(
                    websocket_app(
                        f"ws://{clash.host}:{clash.port}{event}?token={clash.token}&level={clash.log_level}",
                        self.message_queue),
                    name=f'websocket_{clash.host}:{clash.port}_{event.replace("/", "_")}'
                )

    async def post_loki(self, data: dict):
        """post loki

        eg. https://github.com/sleleko/devops-kb/blob/master/python/push-to-loki.py
        """
        for loki_url, loki_user, loki_token in self.loki_info:
            logger.debug('put info to Class: %s', loki_url)
            key = self._post_data(loki_url, loki_user, loki_token)
            await self.push_queue_dict[key].put(data)

    async def parse(self):
        case = {
            'logs': parse_logs,
            'traffic': parse_traffic,
            'tracing': parse_tracing,
        }

        while True:
            data = await self.message_queue.get()
            # noinspection PyArgumentList
            _parse = case.get(data['type'], lambda x: x)(data)
            logger.debug('生成结果：%s', _parse)
            await self.post_loki(_parse)

    async def _push_message(self):
        """数据推送"""
        # TODO: 添加数据推送

    async def _run(self):
        """异步构造函数"""
        # 初始化消息队列
        self.message_queue = asyncio.Queue()
        self.push_queue_dict = defaultdict(asyncio.Queue)

        # 添加WebSocket 监控信息接收 任务
        self.add_websocket_tasks()

        # 添加数据处理任务
        asyncio.create_task(self.parse(), name='parse_message')

        # 添加数据推送任务
        asyncio.create_task(self._push_message(), name='push_message')

        while True:
            print(await self.message_queue.get())

    def run(self, debug=False):
        asyncio.run(self._run(), debug=debug)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(lineno)s - [%(levelname)s] %(message)s'
    )
    monitor = MonitorAsync()
    monitor.add_clash_info('t.leecq.cn', 29090, '123456', 'debug')
    monitor.add_clash_info('192.168.0.4', 29090, '123456', 'debug')
    monitor.run()
