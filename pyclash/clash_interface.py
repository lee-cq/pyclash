#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : clash_interface.py
@Author     : LeeCQ
@Date-Time  : 2022/12/1 23:06
"""

import logging

from pyclash.config_parse import ConfigParse
from pyclash.tools import get_config, set_config

logger = logging.getLogger("pyclash.clash_interface")


class ClashInterface:

    def __init__(self, config_path=None):
        if config_path is None:
            self.config_path = get_config('config_path')
        self.config_path = config_path
        self._config = ConfigParse.from_file(config_path)

    def set_proxy_uri(self, uri):
        set_config('proxy_uri', uri)

    def refresh_config(self):
        uri = get_config('proxy_uri')
        if not uri:
            logger.error('No proxy_uri, please set proxy_uri first')
            raise ValueError('No proxy_uri, please set proxy_uri first')

    def add_rule(self, rule):
        self.verify_rule(rule)
        _rules: list = get_config('parses.prepend_rules')
        if rule in _rules:
            logger.warning(f'Rule {rule} already exists')
            return
        _rules.append(rule)
        set_config('parsers.prepend-rules', rule)

    def verify_rule(self, rule: str):
        """验证规则是否合法"""
        rule_type = rule.split(',')[0]
        if rule_type not in ['DOMAIN-SUFFIX', 'DOMAIN-KEYWORD', 'DOMAIN', 'IP-CIDR', 'GEOIP', 'MATCH']:
            raise ValueError('rule type error')
        proxy = rule.split(',')[-1]
        if proxy not in self._config.proxies or proxy not in self._config.proxy_groups:
            raise ValueError('proxy not in proxies')


if __name__ == '__main__':
    ClashInterface()
