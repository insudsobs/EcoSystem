# -*- coding: utf-8 -*-
"""行情历史：5 分钟周期 OHLC / VWAP / 市场快照。

纯核心实现，不依赖 Minecraft 计时器。Runtime 层监听 OnScriptTickServer
调用 advance_to(now) 驱动周期切换。
"""
from models import new_history_bar
from models import SIDE_BUY, SIDE_SELL


class History(object):
    def __init__(self, period_seconds):
        self._period = period_seconds
        self._current = {}   # item_id -> 当前 bar
        self._closed = {}    # item_id -> [已归档 bar ...]

    def _period_start(self, now):
        return (now // self._period) * self._period

    def _bar(self, item_id, now):
        """获取当前周期 bar，必要时归档旧 bar 并新建。"""
        ps = self._period_start(now)
        bar = self._current.get(item_id)
        if bar is None or bar["period_start"] != ps:
            if bar is not None and bar["trade_count"] > 0:
                self._closed.setdefault(item_id, []).append(bar)
            bar = new_history_bar(item_id, ps)
            self._current[item_id] = bar
        return bar

    def record_trade(self, item_id, price, quantity, side, now):
        """记录一笔成交，更新 OHLC/VWAP/volume/turnover/count。"""
        bar = self._bar(item_id, now)
        if bar["trade_count"] == 0:
            bar["open"] = price
            bar["high"] = price
            bar["low"] = price
        else:
            if price > bar["high"]:
                bar["high"] = price
            if price < bar["low"]:
                bar["low"] = price
        bar["close"] = price
        bar["turnover"] += price * quantity
        if side == SIDE_BUY:
            bar["buy_volume"] += quantity
        else:
            bar["sell_volume"] += quantity
        bar["trade_count"] += 1
        total_volume = bar["buy_volume"] + bar["sell_volume"]
        if total_volume > 0:
            bar["vwap"] = bar["turnover"] // total_volume

    def set_snapshot(self, item_id, market_price, mid_price,
                     system_stock, escrow_stock, now):
        """更新当前周期的市场快照字段。"""
        bar = self._bar(item_id, now)
        bar["market_price"] = market_price
        bar["mid_price"] = mid_price
        bar["system_stock"] = system_stock
        bar["player_escrow_stock"] = escrow_stock

    def advance_to(self, now):
        """关闭所有已越过周期的当前 bar（若其周期已结束）。"""
        ps = self._period_start(now)
        for item_id, bar in list(self._current.items()):
            if bar["period_start"] < ps:
                if bar["trade_count"] > 0:
                    self._closed.setdefault(item_id, []).append(bar)
                # 移除已关闭的当前 bar；下次 record 会按新周期重建
                del self._current[item_id]

    def current_bar(self, item_id):
        return self._current.get(item_id)

    def bars(self, item_id):
        """已归档的完整周期 bar 列表（按周期起点升序）。"""
        return list(self._closed.get(item_id, []))

    def rebuild_from(self, fills):
        """从成交事实重建 OHLC/VWAP/volume（History 是 DERIVED）。

        注意：market_price/mid_price/system_stock/player_escrow_stock 是
        周期末快照，无法从 fills 重建，重建后这些字段为 0。
        """
        self._current = {}
        self._closed = {}
        for f in sorted(fills, key=lambda f: (f["filled_at"], f["fill_id"])):
            self.record_trade(f["item_id"], f["unit_price"], f["quantity"],
                              f["side"], f["filled_at"])

    def snapshot(self):
        """序列化：归档 bar + 当前 bar。"""
        out = []
        for item_id, bars in self._closed.items():
            for b in bars:
                out.append(dict(b))
        for item_id, b in self._current.items():
            out.append(dict(b))
        return out

    @classmethod
    def from_snapshot(cls, bars, period_seconds):
        obj = cls(period_seconds)
        # 按 item_id 分组，每个 item 的 bar 按 period_start 升序；
        # 最后一个（最大 period_start）是当前周期 bar，其余是已归档 bar。
        by_item = {}
        for b in bars:
            b = dict(b)
            by_item.setdefault(b["item_id"], []).append(b)
        for item_id, item_bars in by_item.items():
            item_bars.sort(key=lambda b: b["period_start"])
            for b in item_bars[:-1]:
                obj._closed.setdefault(item_id, []).append(b)
            current = item_bars[-1]
            # 空当前 bar（无成交）丢弃；有成交则作为当前 bar
            if current["trade_count"] > 0:
                obj._current[item_id] = current
        return obj
