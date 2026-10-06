# -*- coding: utf-8 -*-
"""价格引擎：理论价与系统 ask/bid（连续库存惩罚）。

公式（全部整数，禁止 float）：

    midPrice  = P0 * 3T // (2S + T)                  # 理论价/中间价
    systemAsk = max(1, ceil(midPrice * (10000 + spreadBps) / 10000))
    baseBid   = floor(midPrice * (10000 - spreadBps) / 10000)

库存惩罚（连续，替代固定 5%）：

    S <= T              -> inventoryPenaltyBps = 10000（无惩罚）
    T < S < maxStock    -> inventoryPenaltyBps =
                             (maxStock - S) * 10000 // (maxStock - T)
    S >= maxStock       -> systemBid = 0（满仓，停收购，必为 0）

    systemBid = baseBid * inventoryPenaltyBps // 10000

收购开放（S < maxStock）且理论价 midPrice > 0 时，若 bid 因整数取整为 0，
允许最小为 1。midPrice == 0 时不抬价（避免 ask(1) < bid(1) 倒挂与免费套利）。

性质：S 从 T 到 maxStock，penalty 从 10000 线性降到 0，baseBid 亦随 S 上升
而下降，故 bid 单调不增，无价格断崖。
"""
from errors import InvariantViolation


def mid_price(p0, target_stock, system_stock):
    """理论价/中间价。target_stock 必须 > 0，system_stock 必须 >= 0。"""
    if target_stock <= 0:
        raise InvariantViolation("target_stock must be positive: %r" % target_stock)
    if system_stock < 0:
        raise InvariantViolation("system_stock must not be negative: %r" % system_stock)
    return (p0 * 3 * target_stock) // (2 * system_stock + target_stock)


def system_ask(p0, target_stock, system_stock, spread_bps):
    """系统出售价（向上取整，最小 1）。"""
    mid = mid_price(p0, target_stock, system_stock)
    ask = (mid * (10000 + spread_bps) + 9999) // 10000
    return ask if ask >= 1 else 1


def base_bid(p0, target_stock, system_stock, spread_bps):
    """未施加库存惩罚的系统收购价（向下取整）。"""
    mid = mid_price(p0, target_stock, system_stock)
    return (mid * (10000 - spread_bps)) // 10000


def inventory_penalty_bps(target_stock, system_stock, max_stock):
    """连续库存惩罚（bps）。S<=T 无惩罚，T<S<max 线性，S>=max 为 0。"""
    if system_stock <= target_stock:
        return 10000
    if system_stock >= max_stock:
        return 0
    return (max_stock - system_stock) * 10000 // (max_stock - target_stock)


def system_bid(p0, target_stock, system_stock, spread_bps, max_stock):
    """系统收购价（向下取整 + 连续惩罚）。满仓为 0，收购开放且理论价>0 时最小 1。"""
    if system_stock >= max_stock:
        return 0
    mid = mid_price(p0, target_stock, system_stock)
    bid = base_bid(p0, target_stock, system_stock, spread_bps) * \
        inventory_penalty_bps(target_stock, system_stock, max_stock) // 10000
    if bid == 0 and mid > 0:
        bid = 1  # 收购开放且理论价>0 时的最小价
    return bid


def can_system_buy(target_stock, system_stock, max_stock):
    """系统是否继续收购：库存达到 maxStock 后停止收购。"""
    return system_stock < max_stock


class PriceEngine(object):
    """绑定价差与库存上限因子（maxStock = T * factor）的价格引擎。"""

    def __init__(self, spread_bps, max_stock_factor):
        if spread_bps <= 0:
            raise InvariantViolation("spread_bps must be positive: %r" % spread_bps)
        if max_stock_factor <= 1:
            raise InvariantViolation(
                "max_stock_factor must be > 1: %r" % max_stock_factor)
        self.spread_bps = spread_bps
        self.max_stock_factor = max_stock_factor

    def mid(self, p0, target_stock, system_stock):
        return mid_price(p0, target_stock, system_stock)

    def ask(self, p0, target_stock, system_stock):
        return system_ask(p0, target_stock, system_stock, self.spread_bps)

    def bid(self, p0, target_stock, system_stock):
        return system_bid(p0, target_stock, system_stock, self.spread_bps,
                          target_stock * self.max_stock_factor)
