#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : config_parse.py
@Author     : LeeCQ
@Date-Time  : 2022/11/30 22:22

Clash 配置文件解析
"""
import urllib.request

from yaml import safe_load, safe_dump


class ConfigParse:
    """配置文件解析"""
    def __init__(self, config: dict=None):
        self.config = dict() if config is None else config

    @classmethod
    def from_uri(cls, uri: str):
        """从 URI 加载配置"""
        urllib.request.urlretrieve(uri, 'config.yaml')
        with open('config.yaml', 'r', encoding='utf8') as f:
            return cls(safe_load(f))

    @classmethod
    def from_yaml(cls, yaml_str: str):
        """从 YAML 加载配置"""
        _d = safe_load(yaml_str)
        return cls(_d)

    def to_dict(self):
        """转换为字典"""
        return self.config

    def to_yaml(self):
        """转换为 YAML"""
        return safe_dump(self.config, allow_unicode=True)

    def save_yaml(self, file_path: str):
        """保存为 YAML"""
        with open(file_path, 'w', encoding='utf8') as f:
            f.write(self.to_yaml())

    def set_port(self, port: int):
        """设置端口"""
        self.config['port'] = port

    def set_socks_port(self, port: int):
        """设置 SOCKS 端口"""
        self.config['socks-port'] = port

    def set_mix_port(self, port: int):
        """设置混合端口"""
        self.config['mixed-port'] = port

    def set_allow_lan(self, allow: bool):
        """设置是否允许局域网"""
        self.config['allow-lan'] = allow
