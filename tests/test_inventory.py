# -*- coding: utf-8 -*-
import pytest
from inventory import MemoryInventory
from errors import InsufficientStock, ItemNotReceivable, InvalidQuantity


def test_add_and_count():
    inv = MemoryInventory()
    inv.add_item("p", "iron", 10)
    assert inv.count_item("p", "iron") == 10


def test_remove_item():
    inv = MemoryInventory()
    inv.add_item("p", "iron", 10)
    inv.remove_item("p", "iron", 4)
    assert inv.count_item("p", "iron") == 6


def test_remove_insufficient_raises():
    inv = MemoryInventory()
    inv.add_item("p", "iron", 5)
    with pytest.raises(InsufficientStock):
        inv.remove_item("p", "iron", 6)


def test_remove_non_positive_raises():
    inv = MemoryInventory()
    with pytest.raises(InvalidQuantity):
        inv.remove_item("p", "iron", 0)


def test_full_inventory_rejects():
    # 单槽位模型：只放一种物品，堆叠上限 10，槽位 1
    inv = MemoryInventory(max_stack=10, max_slots=1)
    inv.add_item("p", "iron", 10)
    assert inv.can_receive("p", "iron", 1) is False
    with pytest.raises(ItemNotReceivable):
        inv.add_item("p", "iron", 1)


def test_can_receive_same_stack():
    # 单槽背包，堆叠上限 64：60 -> 64 仍占 1 槽，60 -> 65 需 2 槽
    inv = MemoryInventory(max_stack=64, max_slots=1)
    inv.add_item("p", "iron", 60)
    assert inv.can_receive("p", "iron", 4) is True
    assert inv.can_receive("p", "iron", 5) is False  # 超单槽堆叠


def test_snapshot_round_trip():
    inv = MemoryInventory()
    inv.add_item("a", "iron", 10)
    inv.add_item("b", "gold", 3)
    inv2 = MemoryInventory.from_snapshot(inv.snapshot())
    assert inv2.count_item("a", "iron") == 10
    assert inv2.count_item("b", "gold") == 3
