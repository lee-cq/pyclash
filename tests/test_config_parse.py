#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : test_config_parse.py.py
@Author     : LeeCQ
@Date-Time  : 2022/12/1 15:18

测试配置文件解析
"""
import unittest
from pathlib import Path

from pyclash.config_parse import ConfigParse


class TestConfigParse(unittest.TestCase):

    def test_from_yaml(self):
        """测试从yaml文件中解析"""

        config = ConfigParse.from_yaml(
            Path(__file__).parent.joinpath("clash_config/config_bygcloud.yml").read_text(encoding="utf-8")
        )
        # self.assertEqual(config['Proxy'][0]['name'], 'test')

    # def test_from_url(self):
    #     """测试从url中解析"""
    #     config = ConfigParse.from_uri('https://raw.githubusercontent.com/ConnersHua/Profiles/master/Clash/Pro.yaml')
    #     self.assertEqual(config['Proxy'][0]['name'], 'DIRECT')
