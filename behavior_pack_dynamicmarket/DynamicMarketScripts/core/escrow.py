# -*- coding: utf-8 -*-
"""挂单托管（Escrow）。

挂单时物品已从卖家背包移出，进入 escrow，卖家不能继续使用。
成交时从 escrow 消耗，取消/过期时退回卖家背包。
"""
from errors import InsufficientEscrow


class Escrow(object):
    def __init__(self):
        # order_id -> {"seller", "item_id", "amount", "remaining"}
        self._escrow = {}

    def deposit(self, order):
        self._escrow[order["order_id"]] = {
            "seller": order["seller"],
            "item_id": order["item_id"],
            "amount": order["amount"],
            "remaining": order["amount"],
        }

    def remaining(self, order_id):
        entry = self._escrow.get(order_id)
        return entry["remaining"] if entry else 0

    def consume(self, order_id, quantity):
        """成交消耗托管物品，返回该托管的 seller 与 item_id。"""
        entry = self._escrow.get(order_id)
        if entry is None or entry["remaining"] < quantity:
            raise InsufficientEscrow(
                "escrow %r has %r remaining, cannot consume %r"
                % (order_id, entry["remaining"] if entry else 0, quantity))
        entry["remaining"] -= quantity
        return entry["seller"], entry["item_id"]

    def release(self, order_id):
        """结算后清理托管记录。"""
        return self._escrow.pop(order_id, None)

    def total_stock(self, item_id):
        """某物品当前处于玩家托管的总量。"""
        total = 0
        for entry in self._escrow.values():
            if entry["item_id"] == item_id:
                total += entry["remaining"]
        return total

    def snapshot(self):
        out = []
        for order_id, entry in self._escrow.items():
            item = dict(entry)
            item["order_id"] = order_id
            out.append(item)
        return out

    @classmethod
    def from_snapshot(cls, entries):
        obj = cls()
        for item in entries:
            order_id = item["order_id"]
            obj._escrow[order_id] = {
                "seller": item["seller"],
                "item_id": item["item_id"],
                "amount": item["amount"],
                "remaining": item["remaining"],
            }
        return obj
