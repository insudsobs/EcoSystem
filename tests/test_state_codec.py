# -*- coding: utf-8 -*-
import pytest
from state_codec import encode, decode, checksum_of, canonical_dump
from errors import StorageCorrupted, SchemaVersionError
from economy import Economy


def test_round_trip():
    data = {"a": 1, "b": [1, 2, 3], "c": {"d": "str", "e": True}}
    assert decode(encode(data)) == data


def test_checksum_detects_corruption():
    blob = encode({"a": 1})
    blob["data"] = {"a": 2}
    with pytest.raises(StorageCorrupted):
        decode(blob)


def test_newer_schema_rejected():
    blob = {"schemaVersion": 99, "data": {}, "checksum": checksum_of({})}
    with pytest.raises(SchemaVersionError):
        decode(blob)


def test_encode_has_schema_and_saved_at():
    blob = encode({"configVersion": 1, "money": {}}, saved_at=12345)
    assert blob["schemaVersion"] == 1
    assert blob["savedAt"] == 12345
    assert blob["configVersion"] == 1


def test_canonical_dump_stable():
    assert canonical_dump({"a": 1, "b": 2}) == canonical_dump({"b": 2, "a": 1})


def test_market_state_top_level_fields():
    eco = Economy()
    snap = eco.snapshot()
    for key in ("configVersion", "money", "market", "orders", "escrow",
                "claims", "fees", "fills", "history", "inventory", "nextIds"):
        assert key in snap
    assert "quotes" not in snap  # EPHEMERAL，不保存


def test_config_version_preserves_stock():
    eco = Economy()
    eco.inventory.add_item("alice", "iron_ingot", 100)
    eco.sell_to_system("alice", "iron_ingot", 50)  # stock 800 -> 850
    snap = eco.snapshot()
    snap["configVersion"] = 999  # 模拟配置版本变化
    eco2 = Economy()
    eco2.restore(snap)
    assert eco2.market.system_stock("iron_ingot") == 850  # 库存保留


def test_new_item_initialized_on_restore():
    eco = Economy()
    snap = eco.snapshot()
    del snap["market"]["stock"]["iron_ingot"]  # 模拟旧状态缺该商品
    eco2 = Economy()
    eco2.restore(snap)
    assert eco2.market.system_stock("iron_ingot") == \
        eco2.registry.target_stock("iron_ingot")


def test_economy_snapshot_round_trip():
    eco = Economy()
    eco.inventory.add_item("alice", "iron_ingot", 100)
    eco.sell_to_system("alice", "iron_ingot", 50)
    eco.place_sell_order("alice", "iron_ingot", 20, 100)

    snap = eco.snapshot()
    eco2 = Economy()
    eco2.restore(snap)

    assert eco2.market.system_stock("iron_ingot") == \
        eco.market.system_stock("iron_ingot")
    assert eco2.wallet.snapshot() == eco.wallet.snapshot()
    assert eco2.orderbook.snapshot() == eco.orderbook.snapshot()
    assert eco2.monetary.total() == eco.monetary.total()
    eco2.assert_invariants()


def test_economy_save_load_round_trip():
    from storage import MemoryStorage
    eco = Economy()
    eco.inventory.add_item("bob", "diamond", 100)
    eco.sell_to_system("bob", "diamond", 50)

    storage = MemoryStorage()
    eco.save_to(storage)
    eco2 = Economy()
    assert eco2.load_from(storage) is True
    assert eco2.market.system_stock("diamond") == eco.market.system_stock("diamond")
    eco2.assert_invariants()
