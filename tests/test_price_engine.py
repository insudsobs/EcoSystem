# -*- coding: utf-8 -*-
import pytest
from price_engine import (mid_price, system_ask, system_bid, base_bid,
                          inventory_penalty_bps, can_system_buy)

P0 = 100
T = 800
MAX_STOCK = 3 * T
SPREAD = 500


def test_mid_at_target_equals_p0():
    assert mid_price(P0, T, T) == P0


def test_mid_empty_stock():
    assert mid_price(P0, T, 0) == 300


def test_lower_stock_higher_price():
    assert mid_price(P0, T, 100) > mid_price(P0, T, 800) > mid_price(P0, T, 1600)


def test_ask_ceil():
    # mid at S=1200 = 75, ask = ceil(75*1.05) = ceil(78.75) = 79
    assert system_ask(P0, T, 1200, SPREAD) == 79


def test_bid_floor():
    # mid at S=1200 = 75, base_bid = floor(75*0.95) = 71
    assert base_bid(P0, T, 1200, SPREAD) == 71


def test_penalty_at_target_is_100pct():
    assert inventory_penalty_bps(T, T, MAX_STOCK) == 10000


def test_penalty_at_1_5T():
    assert inventory_penalty_bps(T, 1200, MAX_STOCK) == 7500


def test_penalty_at_2T():
    assert inventory_penalty_bps(T, 1600, MAX_STOCK) == 5000


def test_penalty_approaches_zero_near_max():
    assert inventory_penalty_bps(T, MAX_STOCK - 1, MAX_STOCK) < 10


def test_bid_zero_at_max_stock():
    assert system_bid(P0, T, MAX_STOCK, SPREAD, MAX_STOCK) == 0
    # 满仓即使理论 bid 非零也强制为 0
    assert system_bid(P0, T, MAX_STOCK, SPREAD, MAX_STOCK) == 0


def test_bid_min_one_when_open():
    # 接近 maxStock，取整后 bid 为 0，但收购仍开放 -> 最小 1
    assert system_bid(P0, T, MAX_STOCK - 1, SPREAD, MAX_STOCK) == 1


def test_bid_monotonic_decreasing():
    bids = [system_bid(P0, T, s, SPREAD, MAX_STOCK)
            for s in range(T, MAX_STOCK + 1)]
    for i in range(len(bids) - 1):
        assert bids[i] >= bids[i + 1], "bid not monotonic at S=%d" % (T + i)


def test_no_price_cliff():
    # 连续惩罚：S 跨过 T 时 penalty 平滑下降，无固定惩罚的 500bps 断崖
    p_at_t = inventory_penalty_bps(T, T, MAX_STOCK)          # 10000
    p_just_over = inventory_penalty_bps(T, T + 1, MAX_STOCK)  # ~9993
    assert p_at_t - p_just_over < 20  # 相邻差 < 20 bps，无断崖


def test_ask_above_bid():
    for s in (0, 200, 800, 1600, 2399):
        assert system_ask(P0, T, s, SPREAD) > system_bid(P0, T, s, SPREAD, MAX_STOCK)


def test_can_system_buy():
    assert can_system_buy(T, 800, MAX_STOCK) is True
    assert can_system_buy(T, MAX_STOCK - 1, MAX_STOCK) is True
    assert can_system_buy(T, MAX_STOCK, MAX_STOCK) is False


def test_no_ask_bid_inversion_with_tiny_p0():
    # P0=1 时 mid_price 可能为 0，ask 最小 1，bid 在 mid=0 时不 clamp，无倒挂
    assert system_ask(1, 100, 299, 500) >= system_bid(1, 100, 299, 500, 300)
    assert system_ask(2, 100, 260, 500) >= system_bid(2, 100, 260, 500, 300)


def test_spread_bps_zero_raises():
    from price_engine import PriceEngine
    from errors import InvariantViolation
    with pytest.raises(InvariantViolation):
        PriceEngine(0, 3)


def test_target_stock_zero_raises():
    from errors import InvariantViolation
    with pytest.raises(InvariantViolation):
        mid_price(100, 0, 0)


def test_negative_stock_raises():
    from errors import InvariantViolation
    with pytest.raises(InvariantViolation):
        mid_price(100, 800, -1)
