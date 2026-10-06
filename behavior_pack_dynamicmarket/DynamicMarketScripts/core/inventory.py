# -*- coding: utf-8 -*-
"""库存（背包）接口与内存实现。

Inventory 是 core 对玩家物品背包的抽象。Runtime 层用网易 item 组件
（get_item_in_inventory_with_slot / invItemNum / addItems）实现，
Phase 1 仅用 MemoryInventory 做纯核心测试。

注意：网易 SDK 文档未说明背包槽位范围、堆叠上限与 addItems 满包行为，
因此 MemoryInventory 的堆叠/槽位模型是「可调假设」，仅用于驱动核心逻辑的
满包/空间不足分支，不代表真实网易行为（见 docs/RUNTIME_PENDING.md）。
"""
from errors import InvalidQuantity, InsufficientStock, ItemNotReceivable


class Inventory(object):
    """库存接口。item_id 为物品标识（Phase 1 为 RUNTIME_ITEM_ID_PENDING 占位）。"""

    def count_item(self, player_id, item_id):
        raise NotImplementedError

    def can_receive(self, player_id, item_id, amount):
        """是否能接收 amount 个 item（空间/堆叠足够）。"""
        raise NotImplementedError

    def add_item(self, player_id, item_id, amount):
        """加入物品；空间不足抛 ItemNotReceivable。"""
        raise NotImplementedError

    def remove_item(self, player_id, item_id, amount):
        """移除物品；数量不足抛 InsufficientStock。"""
        raise NotImplementedError


class MemoryInventory(Inventory):
    """内存背包。堆叠上限与槽位数为可调假设（真实行为 UNVERIFIED）。"""

    def __init__(self, max_stack=64, max_slots=36):
        self._items = {}            # (player_id, item_id) -> count
        self._max_stack = max_stack
        self._max_slots = max_slots

    def _count(self, player_id, item_id):
        return self._items.get((player_id, item_id), 0)

    def count_item(self, player_id, item_id):
        return self._count(player_id, item_id)

    def _used_slots(self, player_id):
        """该玩家已占用槽位数（按堆叠上限折算）。"""
        used = 0
        for (pid, _item_id), cnt in self._items.items():
            if pid == player_id and cnt > 0:
                used += (cnt + self._max_stack - 1) // self._max_stack
        return used

    def can_receive(self, player_id, item_id, amount):
        if amount <= 0:
            return False
        cnt = self._count(player_id, item_id)
        old_slots = (cnt + self._max_stack - 1) // self._max_stack
        new_slots = (cnt + amount + self._max_stack - 1) // self._max_stack
        added_slots = new_slots - old_slots
        return self._used_slots(player_id) + added_slots <= self._max_slots

    def add_item(self, player_id, item_id, amount):
        if amount <= 0:
            raise InvalidQuantity("add amount must be positive: %r" % amount)
        if not self.can_receive(player_id, item_id, amount):
            raise ItemNotReceivable(
                "player %r cannot receive %r x %r" % (player_id, amount, item_id))
        self._items[(player_id, item_id)] = self._count(player_id, item_id) + amount

    def remove_item(self, player_id, item_id, amount):
        if amount <= 0:
            raise InvalidQuantity("remove amount must be positive: %r" % amount)
        cnt = self._count(player_id, item_id)
        if cnt < amount:
            raise InsufficientStock(
                "player %r has %r x %r, cannot remove %r"
                % (player_id, cnt, item_id, amount))
        remaining = cnt - amount
        if remaining == 0:
            del self._items[(player_id, item_id)]
        else:
            self._items[(player_id, item_id)] = remaining

    def snapshot(self):
        # 转为可序列化结构: {player_id: {item_id: count}}
        out = {}
        for (pid, item_id), cnt in self._items.items():
            out.setdefault(pid, {})[item_id] = cnt
        return out

    @classmethod
    def from_snapshot(cls, data, max_stack=64, max_slots=36):
        obj = cls(max_stack=max_stack, max_slots=max_slots)
        for pid, items in data.items():
            for item_id, cnt in items.items():
                obj._items[(pid, item_id)] = cnt
        return obj
