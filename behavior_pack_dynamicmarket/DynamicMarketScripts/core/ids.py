# -*- coding: utf-8 -*-
"""单调递增 ID 生成器。

orderId / quoteId / fillId / claimId 均使用整数，单调递增，保证排序稳定
（订单簿的时间优先、ID 优先排序依赖此性质）。持久化后可恢复计数。
"""


class IdGenerator(object):
    """从 start 开始单调递增的整数 ID 生成器。"""

    def __init__(self, start=1):
        self._next = start

    def next(self):
        value = self._next
        self._next += 1
        return value

    def ensure_above(self, value):
        """持久化恢复时保证下一次 next() 大于已存在的最大 ID。"""
        if value >= self._next:
            self._next = value + 1

    def current(self):
        return self._next
