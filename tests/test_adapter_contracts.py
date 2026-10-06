# -*- coding: utf-8 -*-
"""Adapter 契约测试：所有 Memory 实现必须通过同一套契约。

未来拿到 MC Studio 后，Netease 实现用同一套契约思路做 Runtime Smoke，
但 Mac 现在不 fake Netease test。
"""
import pytest
from wallet import MemoryWallet
from inventory import MemoryInventory
from storage import MemoryStorage
from identity import MemoryIdentityProvider
from clock import ManualClock
from errors import InsufficientFunds, InsufficientStock, ItemNotReceivable, InvalidQuantity


def test_wallet_contract():
    w = MemoryWallet()
    assert w.balance("a") == 0
    w.credit("a", 100)
    assert w.balance("a") == 100
    w.debit("a", 40)
    assert w.balance("a") == 60
    with pytest.raises(InsufficientFunds):
        w.debit("a", 1000)
    with pytest.raises(InvalidQuantity):
        w.credit("a", -1)
    assert w.total_balance() == 60


def test_inventory_contract():
    inv = MemoryInventory()
    assert inv.count_item("a", "x") == 0
    inv.add_item("a", "x", 10)
    assert inv.count_item("a", "x") == 10
    inv.remove_item("a", "x", 4)
    assert inv.count_item("a", "x") == 6
    with pytest.raises(InsufficientStock):
        inv.remove_item("a", "x", 100)
    assert inv.can_receive("a", "x", 4) is True


def test_inventory_full_contract():
    inv = MemoryInventory(max_stack=10, max_slots=1)
    inv.add_item("a", "x", 10)
    with pytest.raises(ItemNotReceivable):
        inv.add_item("a", "x", 1)


def test_storage_contract():
    s = MemoryStorage()
    assert s.load() is None
    s.save({"k": 1})
    assert s.load() == {"k": 1}


def test_identity_contract():
    p = MemoryIdentityProvider()
    assert p.resolve_account("unknown") is None
    p.bind("s1", "a1")
    assert p.resolve_account("s1") == "a1"
    assert p.resolve_session("s1") == "s1"
    assert p.is_persistence_verified() is True


def test_clock_contract():
    c = ManualClock(100)
    assert c.now() == 100
    c.advance(50)
    assert c.now() == 150
