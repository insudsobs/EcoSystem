# -*- coding: utf-8 -*-
"""时钟抽象。

核心经济逻辑不直接读取真实时间，而是通过 Clock 注入 now（整数秒），
这样纯核心可在 Mac 上用 ManualClock 确定性测试。Runtime 层用
OnScriptTickServer 计数推进一个等价时钟（真实时间源 UNVERIFIED）。
"""


class Clock(object):
    """时间源接口，返回整数秒。"""

    def now(self):
        raise NotImplementedError


class ManualClock(Clock):
    """可手动推进的时钟，用于测试。"""

    def __init__(self, start=0):
        self._now = start

    def now(self):
        return self._now

    def advance(self, seconds):
        self._now += seconds
        return self._now

    def set(self, value):
        self._now = value
        return self._now


class SystemClock(Clock):
    """真实时间时钟（time.time()）。纯 Python 环境可用。

    Runtime 是否直接使用 time.time() 待 MC Studio 验证；若网易 Python
    环境无 time 模块，Runtime 可用 OnScriptTickServer 驱动自己的
    monotonic clock。core 不关心时间来源。
    """

    def now(self):
        import time
        return int(time.time())
