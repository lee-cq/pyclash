#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : test_update_proxies.py
@Author     : LeeCQ
@Date-Time  : 2023/2/7 23:41
"""
import tempfile
from pathlib import Path
from subprocess import run

import pytest
from pyclash.update_proxies import UpdateProxies


def test_update_proxies():
    """update"""
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        clash_file = tdp.joinpath('config.yaml')
        clash_file.write_text(
            '\nport: 27890'
            '\nsocks-port: 27891'
            '\nallow-lan: true'
            '\nmode: Rule'
            '\nlog-level: info'
            '\nexternal-controller: 29090'
        )
        UpdateProxies(
            clash_config=clash_file,
            subscription_url='https://www.efcloud.cc/api/v1/client/subscribe?token=13478b96595061e2d3f63a8880fd3e23'
        )
        print(clash_file.read_text(encoding='utf8'))
        assert 'proxies' in clash_file.read_text(encoding='utf8')


# TODO 补全UpdateProxyGroup Test