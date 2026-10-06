# -*- coding: utf-8 -*-
"""钱包接口与内存实现。

Wallet 是 core 对货币账户的抽象。Runtime 层用网易 extraData 持久化，
Phase 1 仅用 MemoryWallet 做纯核心测试。
"""
from errors import InvalidQuantity, InsufficientFunds


class Wallet(object):
    """钱包接口。实现必须保证余额与 MoneySupply 之间的守恒。"""

    def balance(self, player_id):
        raise NotImplementedError

    def credit(self, player_id, amount):
        """入账（余额增加）。"""
        raise NotImplementedError

    def debit(self, player_id, amount):
        """出账（余额减少），不足时抛 InsufficientFunds。"""
        raise NotImplementedError

    def total_balance(self):
        """所有账户余额之和（用于守恒校验）。"""
        raise NotImplementedError


class MemoryWallet(Wallet):
    """内存钱包，用于纯核心测试。"""

    def __init__(self):
        self._balances = {}

    def balance(self, player_id):
        return self._balances.get(player_id, 0)

    def credit(self, player_id, amount):
        if amount < 0:
            raise InvalidQuantity("credit amount must not be negative: %r" % amount)
        if amount == 0:
            return
        self._balances[player_id] = self.balance(player_id) + amount

    def debit(self, player_id, amount):
        if amount < 0:
            raise InvalidQuantity("debit amount must not be negative: %r" % amount)
        if amount == 0:
            return
        current = self.balance(player_id)
        if current < amount:
            raise InsufficientFunds(
                "player %r balance %r insufficient for debit %r"
                % (player_id, current, amount))
        self._balances[player_id] = current - amount

    def total_balance(self):
        return sum(self._balances.values())

    def snapshot(self):
        return dict(self._balances)

    @classmethod
    def from_snapshot(cls, data):
        obj = cls()
        obj._balances = dict(data)
        return obj
