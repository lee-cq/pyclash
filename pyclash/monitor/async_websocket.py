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
from collections import namedtuple

import aiohttp
import websockets

from pyclash.monitor.data_parse import parse_logs, parse_traffic, parse_tracing

logger = logging.getLogger('pyclash.monitor.async_websocket')


class AsyncQueue(asyncio.Queue):

    def __init__(self, maxsize=0, *, loop=None):
        super().__init__(maxsize=maxsize, loop=loop)
        self.count_put = 0
        self.count_get = 0

    def get_all(self):
        """获取所有消息"""

        def _get_all():
            while not self.empty():
                yield self.get_nowait()

        return [i for i in _get_all()]

    def put_nowait(self, item) -> None:
        """Put an item into the queue without blocking. """
        self.count_put += 1
        return super().put_nowait(item)

    def get_nowait(self):
        """Remove and return an item from the queue without blocking.
        Only get an item if one is immediately available.
        """
        self.count_get += 1
        return super().get_nowait()


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

        self.count_push_request = 0
        self.count_push_request_error = 0

    @property
    def count_received_message(self):
        return self.message_queue.count_get

    @property
    def count_pushed_message(self):
        return self.push_queue.count_put

    @property
    def count_pushed_error_message(self):
        return self.push_error_queue.count_get

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
            await self.push_queue.put(_parse)

    async def _post(self, session: aiohttp.ClientSession, url, user, token, data_s):
        """异步推送数据"""

        async with session.post(url, json={'streams': data_s}, auth=(user, token)) as resp:
            logger.info('推送数据到Loki: %s, %s', url, resp.status)
            if resp.status != 204:
                self.count_push_request_error += 1
                await self.push_error_queue.put(resp) # fixme: 未处理

    async def post_loki(self):
        """数据推送"""
        # TODO: 添加数据推送
        logger.info('start PushToLokiSync in Thread: %s', '')

        async with aiohttp.ClientSession() as session:
            while True:

                # for i in  asyncio.all_tasks() if i.name == 'push_message':

                data_s = self.push_queue.get_all()

                for url, user, token in self.loki_info:
                    logger.info('开始推送数据到Loki: %s', url)
                    host = urllib.parse.urlparse(url).netloc
                    sum(1 for i in asyncio.all_tasks()
                        if i.get_name().startswith(f'loki_push_{host}')) # fixme: 未处理

                    asyncio.create_task(self._post(session, url, user, token, data_s),
                                        name=f'loki_push_{host}')
                    self.count_push_request += 1

    async def _run(self):
        """异步构造函数"""
        # 初始化消息队列
        self.message_queue = AsyncQueue()
        self.push_queue = AsyncQueue()
        self.push_error_queue = AsyncQueue()

        # 添加WebSocket 监控信息接收 任务
        self.add_websocket_tasks()

        # 添加数据处理任务
        asyncio.create_task(self.parse(), name='parse_message')

        # 添加数据推送任务
        asyncio.create_task(self.post_loki(), name='push_message')

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
