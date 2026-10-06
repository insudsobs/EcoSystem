# -*- coding: utf-8 -*-
"""成交事实存储（FillStore）。

Fill 是 AUTHORITATIVE（成交事实），与 History（DERIVED，可重建）分离。
History 可从 Fill 重建（rebuild），反之不可。
"""
from models import new_trade_fill


class FillStore(object):
    """成交记录存储接口。"""

    def append(self, fill):
        raise NotImplementedError

    def get_by_id(self, fill_id):
        raise NotImplementedError

    def get_by_item(self, item_id):
        raise NotImplementedError

    def get_range(self, start_time, end_time):
        """按 filled_at 半开区间 [start_time, end_time) 查询。"""
        raise NotImplementedError

    def all(self):
        raise NotImplementedError

    def count(self):
        raise NotImplementedError


class MemoryFillStore(FillStore):
    def __init__(self, id_generator):
        self._id_gen = id_generator
        self._fills = {}    # fill_id -> fill
        self._order = []    # fill_id 按插入顺序

    def append(self, fill):
        self._fills[fill["fill_id"]] = fill
        self._order.append(fill["fill_id"])
        return fill

    def record(self, item_id, buyer, seller, source, order_id, quantity,
               unit_price, gross, fee, side, filled_at):
        """生成并追加一笔成交事实。"""
        fill = new_trade_fill(self._id_gen.next(), item_id, buyer, seller,
                              source, order_id, quantity, unit_price, gross,
                              fee, side, filled_at)
        return self.append(fill)

    def get_by_id(self, fill_id):
        return self._fills.get(fill_id)

    def get_by_item(self, item_id):
        return [self._fills[fid] for fid in self._order
                if self._fills[fid]["item_id"] == item_id]

    def get_range(self, start_time, end_time):
        return [self._fills[fid] for fid in self._order
                if start_time <= self._fills[fid]["filled_at"] < end_time]

    def all(self):
        return [self._fills[fid] for fid in self._order]

    def count(self):
        return len(self._order)

    def snapshot(self):
        return [dict(f) for f in self.all()]

    @classmethod
    def from_snapshot(cls, fills, id_generator):
        obj = cls(id_generator)
        ordered = sorted(fills, key=lambda f: (f["filled_at"], f["fill_id"]))
        for f in ordered:
            obj.append(dict(f))
        max_id = max([f["fill_id"] for f in fills] or [0])
        obj._id_gen.ensure_above(max_id)
        return obj
