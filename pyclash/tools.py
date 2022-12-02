#!/bin/env python3
"""Cash Config 脚本 Python实现


"""
import os
import logging
import subprocess
from pathlib import Path

from yaml import safe_dump, safe_load, YAMLError

logger = logging.getLogger("pyclash.tools")

SCRIPT_DIR = Path(__file__).absolute().parent
CLASH_WORKDIR = SCRIPT_DIR.parent

os.chdir(CLASH_WORKDIR)


def get_config(key, default=None):
    """从文件中获取配置"""
    PYCLASH_CONFIG = os.environ.get('PYCLASH_CONFIG') or CLASH_WORKDIR.joinpath('pyclash/pyclash_config.yaml')
    PYCLASH_CONFIG = Path(PYCLASH_CONFIG)
    try:
        configs = safe_load(PYCLASH_CONFIG.read_text(encoding='utf8'))
        for k in key.split('.'):
            configs = configs[k]
        logger.debug('Get config success, %s: %s', key, configs)
        return configs

    except FileNotFoundError as _e:
        logger.warning('Get config failed, %s: %s', PYCLASH_CONFIG, _e)
        return default

    except YAMLError as _e:
        logger.warning('Parse YAML failed, %s: %s', PYCLASH_CONFIG, _e)
        return default

    except (KeyError, TypeError) as _e:
        logger.warning(
            'Key: %s Not in File %s, Because of %s, return default value %s',
            key, PYCLASH_CONFIG, _e, default)
        return default


def set_config(key, value):
    """设置值，到配置文件"""
    PYCLASH_CONFIG = os.environ.get('PYCLASH_CONFIG') or CLASH_WORKDIR.joinpath('pyclash/pyclash_config.yaml')
    PYCLASH_CONFIG = Path(PYCLASH_CONFIG)
    try:
        _dic = safe_load(PYCLASH_CONFIG.read_text(encoding='utf8'))
    except (FileNotFoundError, YAMLError):
        _dic = {}

    def update_dic(_dic, _keys, _value):
        """递归更新字典"""
        if len(_keys) == 1:
            _dic[_keys[0]] = _value
        else:
            update_dic(_dic[_keys[0]], _keys[1:], _value)

    update_dic(_dic, key.split('.'), _value=value)
    PYCLASH_CONFIG.write_text(safe_dump(_dic, sort_keys=False), encoding='utf8', )
    logger.info('Save %s : %s to pyclash_config', key, value)


def shell_exec(*cmd, check=False):
    """Shell 执行器"""
    logger.debug('subprocess STDIN: %s', ' '.join(cmd))

    sub_res = subprocess.run(cmd, capture_output=True, check=check)
    _out, _err = sub_res.stdout.decode(), sub_res.stderr.decode()

    logger.debug('subprocess STDOUT: %s', _out)
    logger.debug('subprocess STDERR: %s', _err)

    return sub_res.returncode, _out, _err


if __name__ == '__main__':
    import os

    os.environ['PYCLASH_CONFIG'] = SCRIPT_DIR.parent.joinpath('tests/test_config.yml').as_posix()

    set_config('parsers.prepend-rules', ['test', 'test2'])
    print(get_config('parsers.prepend-rules'))
