# -*- coding: utf-8 -*-
import pytest
from economy import Economy
from errors import InvariantViolation


def test_initial_stock_equals_target():
    eco = Economy()
    for item_id in eco.registry.all_ids():
        assert eco.market.system_stock(item_id) == eco.registry.target_stock(item_id)


def test_decrease_stock_cannot_negative():
    eco = Economy()
    with pytest.raises(InvariantViolation):
        eco.market.decrease_stock("iron_ingot", 10 ** 9)


def test_system_ask_above_bid():
    eco = Economy()
    assert eco.market.system_ask("iron_ingot") > eco.market.system_bid("iron_ingot")


def test_restock_only_supply_goods():
    eco = Economy()
    # 把保供与普通商品的库存都压低到 0，只有保供会补货
    for item_id in eco.registry.all_ids():
        eco.market.decrease_stock(item_id, eco.market.system_stock(item_id))
    restocked = eco.restock()
    restocked_items = {item_id for item_id, _ in restocked}
    assert restocked_items == set(eco.registry.supply_ids())
    for item_id in eco.registry.supply_ids():
        assert eco.market.system_stock(item_id) > 0
    for item_id in eco.registry.all_ids():
        if item_id not in eco.registry.supply_ids():
            assert eco.market.system_stock(item_id) == 0


def test_restock_not_triggered_above_threshold():
    eco = Economy()
    # 库存 = T（高于 30%T 阈值），不应补货
    before = eco.market.system_stock("bread")
    assert eco.restock() == []
    assert eco.market.system_stock("bread") == before


def test_restock_caps_at_target():
    eco = Economy()
    t = eco.registry.target_stock("bread")
    # 压到 29%T（低于 30% 阈值），补货不应超过 T
    eco.market.decrease_stock("bread", t - (t * 29 // 100))
    eco.restock()
    assert eco.market.system_stock("bread") <= t
