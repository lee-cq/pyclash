#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : data_parse.py
@Author     : LeeCQ
@Date-Time  : 2023/2/15 22:55
"""

import json
import logging
import time

logger = logging.getLogger('pyclash.monitor.data_parse')

__all__ = ['Stream', 'parse', 'parse_logs', 'parse_tracing', 'parse_traffic']


# REALIZED_PARSE = {
#     'tracing': parse_tracing,
#     'traffic': parse_traffic,
#     'logs': parse_logs,
# }


class Stream:
    def __init__(self, host: str, type: str, *, job: str = 'clash'):
        self.host = host
        self.type = type
        self.job = job
        self.values = []

    def add_value(self, value: str, timestamp: int = None):
        if timestamp is None:
            timestamp = time.time_ns()
        self.values.append([str(timestamp), str(value)])

    def dict(self) -> dict:
        return {
            "stream": {
                "job": self.job,
                "type": self.type,
                "host": self.host,
            },
            "values": self.values
        }

    def __repr__(self):
        return f'LokiStream(host={self.host}, type={self.type}, job={self.job})'


def parse(data: dict, stream: Stream = None) -> Stream:
    """parse log """
    logger.debug('parse log: %s', data['message'])
    if stream is None:
        stream = Stream(job='clash', host=data['host'], type=data['type'])

    if stream.type != data['type']:
        raise ValueError(f'stream type <{stream.type}> and data type <{data["type"]}> must is different.')

    # TODO: parse data

    _parse = lambda x: json.dumps(json.loads(x), sort_keys=False, ensure_ascii=False)

    stream.add_value(_parse(data['message']), data['timestamp'])

    return stream


def parse_tracing(data: dict) -> dict:
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


def parse_logs(data: dict, stream: Stream = None) -> dict:
    """parse log """
    logger.debug('parse log: %s', data['message'])
    if stream is None:
        stream = Stream(job='clash', host=data['host'], type='log')

    if stream.type != 'log':
        raise ValueError('stream type must be log')

    stream.add_value(data['message'], data['timestamp'])

    return stream.dict()


def parse_traffic(data: dict) -> dict:
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
