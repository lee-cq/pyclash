#!/bin/env python3
"""更新代理
"""
import os
import urllib.request
from yaml import safe_load


class UpdateProxies:
    """Update """

    def __init__(self, clash_config, subscription_url) -> None:
        self.clash_config = clash_config
        self.subscription_url = subscription_url

    def set_http_proxy(self, url):
        """设置HTTP代理地址"""
        os.environ['http_proxy'] = url
        os.environ['https_proxy'] = url

    def download_subscription(self):
        """下载订阅信息"""
        reponse = urllib.request.urlopen(f'https://api.dler.io/sub?target=clash&insert=true&new_name=true&scv=true&udp=true&exclude=&include=&url={self.subscription_url}&config=https://github.com/juewuy/ShellClash/raw/master/rules/ShellClash.ini')
        reponse.text
        

    def update_clash_config(self):
        """更新Clash配置"""
