# -*- coding: utf-8 -*-
"""系统市场状态：每种商品的 systemStock 与价格查询。

只认 logicalId（ItemRegistry），不感知 runtime item identifier。
systemStock 不可为负；库存达到 maxStock(默认 3T) 后系统停止收购。
marketVersion 每次库存/订单变化时递增，用于报价失效检测。
"""
from errors import InvariantViolation, InvalidQuantity


class Market(object):
    def __init__(self, price_engine, registry):
        self._price_engine = price_engine
        self._registry = registry
        self._stock = {}      # logical_id -> system stock
        self._version = 0

    # ---- 库存 ----
    def init_stock(self, item_id, amount):
        self._stock[item_id] = amount

    def reset_all_to_target(self):
        """初始化/重置：每种商品 systemStock = 目标库存 T。"""
        for item_id in self._registry.all_ids():
            self._stock[item_id] = self._registry.target_stock(item_id)

    def system_stock(self, item_id):
        return self._stock.get(item_id, 0)

    def increase_stock(self, item_id, amount):
        """系统库存增加（保供补货 / 玩家卖给系统）。"""
        if amount <= 0:
            raise InvalidQuantity("increase amount must be positive: %r" % amount)
        self._stock[item_id] = self.system_stock(item_id) + amount

    def decrease_stock(self, item_id, amount):
        """系统库存减少（系统出售）。不可为负。"""
        if amount <= 0:
            raise InvalidQuantity("decrease amount must be positive: %r" % amount)
        current = self.system_stock(item_id)
        if current < amount:
            raise InvariantViolation(
                "system stock of %r cannot go negative (have %r, decrease %r)"
                % (item_id, current, amount))
        self._stock[item_id] = current - amount

    # ---- 价格 ----
    def _p0_t(self, item_id):
        return self._registry.p0(item_id), self._registry.target_stock(item_id)

    def system_theoretical(self, item_id):
        p0, t = self._p0_t(item_id)
        return self._price_engine.mid(p0, t, self.system_stock(item_id))

    def system_ask(self, item_id):
        p0, t = self._p0_t(item_id)
        return self._price_engine.ask(p0, t, self.system_stock(item_id))

    def system_bid(self, item_id):
        p0, t = self._p0_t(item_id)
        return self._price_engine.bid(p0, t, self.system_stock(item_id))

    def mid_price(self, item_id):
        p0, t = self._p0_t(item_id)
        return self._price_engine.mid(p0, t, self.system_stock(item_id))

    def can_buy_from_player(self, item_id):
        """系统是否继续收购该物品。"""
        return self.system_stock(item_id) < self._registry.max_stock(item_id)

    # ---- 版本 ----
    def version(self):
        return self._version

    def bump_version(self):
        self._version += 1
        return self._version

    # ---- 快照 ----
    def snapshot(self):
        return dict(self._stock)

    @classmethod
    def from_snapshot(cls, data, price_engine, registry, version):
        obj = cls(price_engine, registry)
        obj._stock = dict(data)
        obj._version = version
        return obj
