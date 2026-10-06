# -*- coding: utf-8 -*-
from economy import Economy
from history import History
from models import SIDE_BUY, SIDE_SELL


def test_fill_store_append_and_get():
    eco = Economy()
    eco.inventory.add_item("alice", "iron_ingot", 100)
    eco.sell_to_system("alice", "iron_ingot", 50)
    store = eco.fill_ledger
    assert store.count() == 1
    fills = store.all()
    assert fills[0]["item_id"] == "iron_ingot"
    assert store.get_by_id(fills[0]["fill_id"]) is not None
    assert store.get_by_id(99999) is None


def test_fill_store_get_by_item():
    eco = Economy()
    eco.inventory.add_item("alice", "iron_ingot", 100)
    eco.sell_to_system("alice", "iron_ingot", 50)
    eco.inventory.add_item("alice", "diamond", 100)
    eco.sell_to_system("alice", "diamond", 50)
    store = eco.fill_ledger
    assert len(store.get_by_item("iron_ingot")) == 1
    assert len(store.get_by_item("diamond")) == 1


def test_fill_store_get_range():
    eco = Economy()
    eco.inventory.add_item("alice", "iron_ingot", 100)
    eco.sell_to_system("alice", "iron_ingot", 10, now=100)
    eco.sell_to_system("alice", "iron_ingot", 10, now=200)
    store = eco.fill_ledger
    assert len(store.get_range(0, 150)) == 1
    assert len(store.get_range(150, 300)) == 1


def test_fill_has_side():
    eco = Economy()
    eco.inventory.add_item("alice", "iron_ingot", 100)
    eco.sell_to_system("alice", "iron_ingot", 10)
    assert eco.fill_ledger.all()[0]["side"] == SIDE_SELL


def test_rebuild_history_from_fills():
    eco = Economy()
    eco.inventory.add_item("alice", "iron_ingot", 100)
    eco.sell_to_system("alice", "iron_ingot", 50, now=0)

    fresh = History(300)
    fresh.rebuild_from(eco.fill_ledger.all())
    bar = fresh.current_bar("iron_ingot")
    assert bar["sell_volume"] == 50
    assert bar["trade_count"] == 1


def test_history_and_fill_separated():
    eco = Economy()
    eco.inventory.add_item("alice", "iron_ingot", 100)
    eco.sell_to_system("alice", "iron_ingot", 50)
    fills_before = eco.fill_ledger.count()
    # 清空 history 不影响 fills（Fill 是事实，History 是派生）
    eco.history.advance_to(10 ** 9)
    assert eco.fill_ledger.count() == fills_before
