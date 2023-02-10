#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : update_rules.py
@Author     : LeeCQ
@Date-Time  : 2023/2/9 11:50

"""
import logging

from update_base import *

logger = logging.getLogger('pyclash.update.rules')


class UpdateRules:
    """更新规则"""

    def __init__(self):
        pass

    def from_provider(self):
        """从 rule_provider 更新规则

        提供商如果存在于config中。
        """
