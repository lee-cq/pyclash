#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : test_tools.py
@Author     : LeeCQ
@Date-Time  : 2022/12/2 14:35
"""
import os
import unittest
from pathlib import Path

from pyclash.tools import get_config, set_config

TEST_DIR = Path(__file__).parent


class TestTools(unittest.TestCase):
    OLD_CONFIG = os.environ.get('PYCLASH_CONFIG')

    @classmethod
    def setUpClass(cls) -> None:

        os.environ['PYCLASH_CONFIG'] = 'tests/test_config.yml'

        open('tests/test_config.yml', 'w', encoding='utf8').write(
            open(TEST_DIR.parent / 'pyclash/pyclash_config_default.yaml', 'r', encoding='utf8').read()
        )

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.OLD_CONFIG:
            os.environ['PYCLASH_CONFIG'] = cls.OLD_CONFIG
        else:
            del os.environ['PYCLASH_CONFIG']

        # Path('tests/test_config.yml').unlink(missing_ok=True)

    def test_set_config(self):
        """测试设置配置"""
        set_config('add_test', 'test')
        self.assertEqual(get_config('add_test'), 'test')

    def test_get_dot_config(self):
        """测试获取配置"""
        self.assertIsInstance(get_config('parsers.prepend-rules'), list)

    def test_set_dot_config(self):
        """测试设置配置"""
        set_config('parsers.prepend-rules', ['test'])
        self.assertEqual(get_config('parsers.prepend-rules'), ['test'])
