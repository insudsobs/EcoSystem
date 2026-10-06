# -*- coding: utf-8 -*-
"""pytest 公共配置：把 core 目录加入 sys.path，便于 import 纯核心模块。"""
import os
import sys

CORE_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'behavior_pack_dynamicmarket',
    'DynamicMarketScripts', 'core'))

COMMON_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'behavior_pack_dynamicmarket',
    'DynamicMarketScripts', 'common'))

for d in (CORE_DIR, COMMON_DIR):
    if d not in sys.path:
        sys.path.insert(0, d)
