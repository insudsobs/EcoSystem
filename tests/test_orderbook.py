# -*- coding: utf-8 -*-
from models import new_sell_order
from orderbook import OrderBook


def test_price_priority():
    ob = OrderBook()
    ob.add(new_sell_order(1, "a", "iron", 10, 100, 0))
    ob.add(new_sell_order(2, "b", "iron", 10, 90, 0))
    ob.add(new_sell_order(3, "c", "iron", 10, 110, 0))
    assert ob.best_open("iron")["order_id"] == 2  # 最低价 90


def test_time_priority():
    ob = OrderBook()
    ob.add(new_sell_order(1, "a", "iron", 10, 100, 10))
    ob.add(new_sell_order(2, "b", "iron", 10, 100, 5))
    assert ob.best_open("iron")["order_id"] == 2  # 同价，时间早优先


def test_id_priority():
    ob = OrderBook()
    ob.add(new_sell_order(2, "b", "iron", 10, 100, 5))
    ob.add(new_sell_order(1, "a", "iron", 10, 100, 5))
    assert ob.best_open("iron")["order_id"] == 1  # 同价同时，id 小优先


def test_open_orders_sorted():
    ob = OrderBook()
    ob.add(new_sell_order(1, "a", "iron", 10, 100, 10))
    ob.add(new_sell_order(2, "b", "iron", 10, 80, 0))
    ob.add(new_sell_order(3, "c", "iron", 10, 90, 0))
    prices = [o["unit_price"] for o in ob.open_orders("iron")]
    assert prices == [80, 90, 100]


def test_remove():
    ob = OrderBook()
    ob.add(new_sell_order(1, "a", "iron", 10, 100, 0))
    ob.remove(1)
    assert ob.best_open("iron") is None
