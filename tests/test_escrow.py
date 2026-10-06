# -*- coding: utf-8 -*-
import pytest
from models import new_sell_order
from escrow import Escrow
from errors import InsufficientEscrow


def test_deposit_and_consume():
    e = Escrow()
    e.deposit(new_sell_order(1, "a", "iron", 10, 100, 0))
    assert e.remaining(1) == 10
    seller, item = e.consume(1, 4)
    assert seller == "a"
    assert item == "iron"
    assert e.remaining(1) == 6


def test_consume_insufficient():
    e = Escrow()
    e.deposit(new_sell_order(1, "a", "iron", 5, 100, 0))
    with pytest.raises(InsufficientEscrow):
        e.consume(1, 6)


def test_release():
    e = Escrow()
    e.deposit(new_sell_order(1, "a", "iron", 10, 100, 0))
    entry = e.release(1)
    assert entry["remaining"] == 10
    assert e.remaining(1) == 0


def test_total_stock():
    e = Escrow()
    e.deposit(new_sell_order(1, "a", "iron", 10, 100, 0))
    e.deposit(new_sell_order(2, "b", "iron", 5, 100, 0))
    e.deposit(new_sell_order(3, "c", "gold", 7, 100, 0))
    assert e.total_stock("iron") == 15
    assert e.total_stock("gold") == 7
