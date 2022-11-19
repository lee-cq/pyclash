#!/bin/env python3
"""Cash Config 脚本 Python实现


"""
import os
import logging
import subprocess
from pathlib import Path

from yaml import safe_dump, safe_load, YAMLError

logger = logging.getLogger("pyclash.config")

SCRIPT_DIR = Path(__file__).absolute().parent
CLASH_WORKDIR = SCRIPT_DIR.parent

os.chdir(CLASH_WORKDIR)


def get_config(key, defualt=None) -> str:
    """从文件中获取配置"""
    pyclash_config = SCRIPT_DIR.joinpath('pyclash_config.yaml')

    try:
        configs = safe_load(pyclash_config.read_text(encoding='utf8'))
        for k in key.split('.'):
            configs = configs[k]
        logger.debug('Get config success, %s: %s', key, configs)
        return configs

    except (FileNotFoundError, YAMLError, KeyError) as _e:
        logger.warning(
            'Key: %s Not File, Because of %s, return defuat value %s',
            key, _e, defualt)
        return defualt


def set_config(key, value):
    """设置值，到配置文件"""
    pyclash_config = SCRIPT_DIR.joinpath('pyclash_config.yaml')
    try:
        _js = safe_load(pyclash_config.read_text(encoding='utf8'))
    except (FileNotFoundError, YAMLError, KeyError):
        _js = {}

    _js[key] = value

    pyclash_config.write_text(safe_dump(_js), encoding='utf8')
    logger.info('Save %s : %s to pyclashconfig', key, value)


def shell_exec(*cmd, check=False):
    """Shell 执行器"""
    logger.debug('subprocess STDIN: %s', ' '.join(cmd))

    sub_res = subprocess.run(cmd, capture_output=True, check=check)
    _out, _err = sub_res.stdout.decode(), sub_res.stderr.decode()

    logger.debug('subprocess STDOUT: %s', _out)
    logger.debug('subprocess STDERR: %s', _err)

    return sub_res.returncode, _out, _err


def install_clash_core(clash_type, clash_version):
    """安装Clash Type"""
    # TODO 多源支持
    download_url = get_config(f'clash_core.{clash_type}.{clash_version}')

    if not download_url:
        raise ValueError('download url is None.')

    shell_exec('wget', '-O', 'clash.gz', download_url, check=True)
    shell_exec('gzip', '-d', 'clash.gz', check=True)
    os.chmod('clash', 555)


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
