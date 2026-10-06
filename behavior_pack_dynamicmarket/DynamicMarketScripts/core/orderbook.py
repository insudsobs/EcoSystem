# -*- coding: utf-8 -*-
"""玩家卖单簿。

维护每个 item 的卖单，按 unitPrice asc -> createdAt asc -> orderId asc 排序。
撮合时从最低价开始消费。
"""
from sell_order import sort_key, is_open
from errors import OrderNotFound


class OrderBook(object):
    def __init__(self):
        self._orders = {}       # order_id -> order
        self._by_item = {}      # item_id -> [order_id ...] 已排序

    def add(self, order):
        oid = order["order_id"]
        self._orders[oid] = order
        lst = self._by_item.setdefault(order["item_id"], [])
        lst.append(oid)
        lst.sort(key=lambda o: sort_key(self._orders[o]))

    def remove(self, order_id):
        order = self._orders.pop(order_id, None)
        if order is None:
            raise OrderNotFound("order %r not found" % order_id)
        lst = self._by_item[order["item_id"]]
        lst.remove(order_id)
        if not lst:
            del self._by_item[order["item_id"]]
        return order

    def get(self, order_id):
        return self._orders.get(order_id)

    def best_open(self, item_id):
        """最低价的 OPEN 卖单，无则返回 None。"""
        for oid in self._by_item.get(item_id, []):
            order = self._orders[oid]
            if is_open(order):
                return order
        return None

    def open_orders(self, item_id):
        """按排序返回 item 的全部 OPEN 卖单。"""
        return [self._orders[oid] for oid in self._by_item.get(item_id, [])
                if is_open(self._orders[oid])]

    def all_orders(self):
        return list(self._orders.values())

    def open_orders_all(self):
        return [o for o in self._orders.values() if is_open(o)]

    def count_open(self, item_id):
        return len(self.open_orders(item_id))

    def snapshot(self):
        return [dict(o) for o in self._orders.values()]

    @classmethod
    def from_snapshot(cls, orders):
        obj = cls()
        for order in orders:
            obj._orders[order["order_id"]] = order
        # 重建索引并排序
        for order in obj._orders.values():
            obj._by_item.setdefault(order["item_id"], []).append(order["order_id"])
        for item_id in obj._by_item:
            obj._by_item[item_id].sort(
                key=lambda o: sort_key(obj._orders[o]))
        return obj
