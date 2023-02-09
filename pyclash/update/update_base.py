#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : update_base.py
@Author     : LeeCQ
@Date-Time  : 2023/2/9 11:50

"""

import logging
import subprocess

from pathlib import Path
from yaml import safe_load, safe_dump

logger = logging.getLogger('pyclash.update.base')

__all__ = ['get_clash_config', 'save_clash_config']


def get_clash_config(config_path) -> dict:
    """获取配置"""
    logger.info('尝试获取配置文件 %s', config_path)
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError()

    data = safe_load(config_path.read_text(encoding='utf8'))
    logger.debug('config data keys %s', data.keys())

    return data


def check_clash_config(config_path) -> bool:
    """检查配置文件是否正确"""
    clash_dir = Path(config_path).parent

    r = subprocess.run([str(clash_dir.parent.joinpath('clash')),
                        '-d', clash_dir.as_posix(),
                        '-f', str(config_path),
                        '-t'
                        ], capture_output=True)
    if r.returncode == 0:
        return True
    else:
        logger.error('Clash Config Error: \n%s', r.stderr.decode())
        return False


def save_clash_config(config_path, dic) -> int:
    """保存配置"""
    new_config = safe_dump(
        dic,
        allow_unicode=True,
        sort_keys=False,
    )

    config_path = Path(config_path)
    config_path_bak = Path(str(config_path) + '-')  # 定义配置备份文件
    config_path_bak.write_bytes(config_path.read_bytes())  # 备份原始config

    config_path.write_text(new_config, encoding='utf8')  # 写入新配置

    if not check_clash_config(config_path):
        logger.info('Config Error, Will con config')
        config_path.write_bytes(config_path_bak.read_bytes())
        return 1
    else:
        logger.info('Config Update Success. %s', config_path)
