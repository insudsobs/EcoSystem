# -*- coding: utf-8 -*-
"""手续费累积器。

玩家订单成交手续费 1%（可配），卖家承担，fee 从 MoneySupply 销毁。
手续费余数按 seller 累积（而非按订单），防止小额拆分交易逃避手续费。

例（fee_bps=100，即 1%）：
    gross=150 单笔 -> fee=1
    拆成 50+50+50 -> 前两笔 fee=0（余数累积），第三笔进位 fee=1，总 fee=1，等价。
"""


class FeeAccumulator(object):
    def __init__(self, fee_bps):
        self.fee_bps = fee_bps
        self._remainder = {}  # seller -> 累积余数(单位: bps)

    def charge(self, seller, gross):
        """计算并累积手续费，返回本笔应扣 fee。"""
        total_units = gross * self.fee_bps
        fee = total_units // 10000
        remainder = total_units % 10000
        self._remainder[seller] = self._remainder.get(seller, 0) + remainder
        extra = self._remainder[seller] // 10000
        if extra:
            fee += extra
            self._remainder[seller] %= 10000
        return fee

    def net(self, seller, gross):
        """卖家实得 = gross - fee。"""
        return gross - self.charge(seller, gross)

    def remainder(self, seller):
        return self._remainder.get(seller, 0)

    def snapshot(self):
        return dict(self._remainder)

    @classmethod
    def from_snapshot(cls, data, fee_bps):
        obj = cls(fee_bps)
        obj._remainder = dict(data)
        return obj
