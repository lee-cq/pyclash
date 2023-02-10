#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : update_proxies.py
@Author     : LeeCQ
@Date-Time  : 2023/2/8 21:50

更新代理
"""
import logging
import os
from pathlib import Path

from requests import get
from yaml import safe_load

from pyclash.update.update_base import get_clash_config, save_clash_config

logger = logging.getLogger('pyclash.update.proxies')


class UpdateProxies:
    """Update """

    def __init__(self, clash_config, subscription_url, merge=False) -> None:
        self.clash_config = Path(clash_config)
        self.subscription_url = subscription_url
        self.merge = merge

        if not self.clash_config.exists():
            raise FileNotFoundError(self.clash_config)

        self.update_clash_config()
        self.update_proxy_groups()

    @staticmethod
    def set_http_proxy(url):
        """设置HTTP代理地址"""
        if get('https://google.com', proxies={'https': url, 'http': url}, timeout=5).status_code != 200:
            return

        os.environ['http_proxy'] = url
        os.environ['https_proxy'] = url

    def download_subscription(self):
        """下载订阅信息"""
        if '&flag=clash' not in self.subscription_url:
            self.subscription_url += '&flag=clash'
        response = get(self.subscription_url,
                       headers={
                           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                         'Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.78'
                       }
                       )
        if response.status_code // 100 == 2:
            return response.text
        else:
            raise ValueError(f"HTTP 非 200 返回, ({response.status_code=}, {response.url=} \n"
                             f"\n{response.headers=}"
                             f"\n{response.text})")  # TODO HTTP ERROR

    @property
    def new_proxies(self):
        new_proxies = safe_load(self.download_subscription()).get('proxies', [])
        if not new_proxies:
            raise  # TODO 未发现新的代理
        return new_proxies

    def update_clash_config(self):
        """"""
        dic_config = get_clash_config(self.clash_config)

        if self.merge:
            _proxies = set(dic_config.get('proxies', [])) | self.new_proxies
        else:
            _proxies = self.new_proxies

        dic_config['proxies'] = _proxies
        save_clash_config(self.clash_config, dic_config)

    def update_proxy_groups(self):
        """更新代理组信息"""

        def update_group(group, proxies, providers):
            group['proxies'] = proxies
            group['ues'] = providers
            return group

        dic_config = safe_load(self.clash_config.read_text(encoding='utf8'))
        proxy_groups = dic_config.get('proxy-groups', [])

        proxy_providers_name = [i.get('name') for i in dic_config.get('proxy-providers', [])]
        all_proxies_name = [i.get('name') for i in dic_config.get('proxies')]

        dic_config['proxy-groups'] = [
            update_group(group, all_proxies_name, proxy_providers_name) for group in proxy_groups
        ]
        print(dic_config['proxy-groups'])
        save_clash_config(self.clash_config, dic_config)


if __name__ == '__main__':
    file_dir = Path(__file__).parent
    UpdateProxies(
        clash_config=file_dir / 'config.yaml',
        subscription_url="https://www.efcloud.cc/api/v1/client/subscribe?"
                         "token=13478b96595061e2d3f63a8880fd3e23&flag=clash"
    )
