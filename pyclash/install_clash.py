#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : install_clash.py
@Author     : LeeCQ
@Date-Time  : 2022/12/1 22:23

安装clash
"""
import logging
import urllib.request
from pathlib import Path

from tools import shell_exec, get_config, set_config

logger = logging.getLogger('pyclash.install')


class Install:
    """安装"""

    def __init__(self, install_dir):
        install_dir = Path(install_dir)
        if Path(install_dir).is_file():
            raise ValueError('install_dir is not a directory')
        install_dir.mkdir(parents=True, exist_ok=True)

        self.install_dir = install_dir

    def install_clash(self, clash_type, version, os, platform):
        """安装Clash Type"""
        # TODO 多源支持
        download_url = get_config(f'clash_core.{clash_type}.{version}.{os}.{platform}')
        urllib.request.urlretrieve(download_url, self.install_dir.joinpath('clash'))

    def install_clash_dash(dash_type, version):
        """安装面板"""


if __name__ == '__main__':
    logger.setLevel('DEBUG')
    fmt = logging.Formatter('[%(asctime)s] %(levelname)s %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(fmt=fmt)
    handler.setLevel('DEBUG')
    logger.addHandler(handler)

    install_clash_core('premium', 'latest')
