# -*- coding: utf-8 -*-
from economy import Economy
from models import SIDE_BUY, SIDE_SELL


def test_ohlc():
    eco = Economy()
    h = eco.history
    h.record_trade("iron", 100, 10, SIDE_BUY, 0)
    h.record_trade("iron", 110, 5, SIDE_BUY, 0)
    h.record_trade("iron", 90, 3, SIDE_BUY, 0)
    bar = h.current_bar("iron")
    assert bar["open"] == 100
    assert bar["high"] == 110
    assert bar["low"] == 90
    assert bar["close"] == 90


def test_vwap_integer():
    eco = Economy()
    h = eco.history
    h.record_trade("iron", 100, 10, SIDE_BUY, 0)   # turnover 1000
    h.record_trade("iron", 200, 10, SIDE_BUY, 0)   # turnover 2000
    bar = h.current_bar("iron")
    assert bar["turnover"] == 3000
    assert bar["vwap"] == 150  # 3000 // 20


def test_volume_by_side():
    eco = Economy()
    h = eco.history
    h.record_trade("iron", 100, 10, SIDE_BUY, 0)
    h.record_trade("iron", 100, 7, SIDE_SELL, 0)
    bar = h.current_bar("iron")
    assert bar["buy_volume"] == 10
    assert bar["sell_volume"] == 7


def test_period_rollover():
    eco = Economy()
    h = eco.history
    h.record_trade("iron", 100, 10, SIDE_BUY, 0)      # 周期 0
    h.record_trade("iron", 200, 5, SIDE_BUY, 300)     # 周期 300（5 分钟）
    bars = h.bars("iron")
    assert len(bars) == 1
    assert bars[0]["period_start"] == 0
    assert h.current_bar("iron")["period_start"] == 300


def test_advance_to_closes_period():
    eco = Economy()
    h = eco.history
    h.record_trade("iron", 100, 10, SIDE_BUY, 0)
    h.set_snapshot("iron", 100, 100, 800, 0, 0)
    h.advance_to(300)
    assert h.current_bar("iron") is None
    assert len(h.bars("iron")) == 1
