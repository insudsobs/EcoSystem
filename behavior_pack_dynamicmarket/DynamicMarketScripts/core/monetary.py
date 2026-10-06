# -*- coding: utf-8 -*-
"""货币供应量 MoneySupply。

语义：
    玩家卖给系统  -> 系统发行货币（issued 增加）
    玩家从系统购买 -> 系统回收货币（destroyed 增加）
    玩家之间交易  -> 只转移，MoneySupply 不变
    自由市场手续费 -> 销毁货币（destroyed 增加）

不变量：
    total = initial + issued - destroyed，必须 >= 0。
    绝不使用 max(0, ...) 兜底——若计算出现负数，说明存在逻辑错误，
    直接抛 InvariantViolation 暴露问题。
"""
from errors import InvariantViolation


class MoneySupply(object):
    def __init__(self, initial=0):
        self.initial = initial
        self.issued = 0
        self.destroyed = 0

    def issue(self, amount):
        """发行货币（玩家卖给系统）。amount 为负抛异常，0 为 no-op。"""
        if amount < 0:
            raise InvariantViolation("issue amount must not be negative: %r" % amount)
        if amount == 0:
            return
        self.issued += amount

    def destroy(self, amount):
        """销毁货币（手续费/系统回收）。amount 为负抛异常，0 为 no-op，
        不超过现存总量。"""
        if amount < 0:
            raise InvariantViolation("destroy amount must not be negative: %r" % amount)
        if amount == 0:
            return
        if amount > self.total():
            raise InvariantViolation(
                "destroy %r exceeds total money supply %r" % (amount, self.total()))
        self.destroyed += amount

    def total(self):
        """现存货币总量。若为负表示逻辑错误。"""
        return self.initial + self.issued - self.destroyed

    def assert_invariant(self):
        """显式校验不变量，负值抛 InvariantViolation。"""
        if self.total() < 0:
            raise InvariantViolation(
                "money supply went negative: initial=%r issued=%r destroyed=%r"
                % (self.initial, self.issued, self.destroyed))

    def snapshot(self):
        return {
            "initial": self.initial,
            "issued": self.issued,
            "destroyed": self.destroyed,
        }

    @classmethod
    def from_snapshot(cls, data):
        obj = cls(data["initial"])
        obj.issued = data["issued"]
        obj.destroyed = data["destroyed"]
        obj.assert_invariant()
        return obj
