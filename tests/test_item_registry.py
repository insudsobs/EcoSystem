# -*- coding: utf-8 -*-
import pytest
from economy import Economy
from item_registry import build_default_registry, ItemRegistry


def make_registry():
    return build_default_registry(3)


def test_has_27_items():
    r = make_registry()
    assert len(r.all_ids()) == 27


def test_economic_params():
    r = make_registry()
    assert r.p0("iron_ingot") == 100
    assert r.target_stock("iron_ingot") == 800
    assert r.max_stock("iron_ingot") == 2400


def test_dirt_runtime_verified():
    # dirt 在 20190712 文档中明确出现 minecraft:dirt
    r = make_registry()
    assert r.runtime_item_id("dirt") == "minecraft:dirt"
    assert r.is_runtime_verified("dirt") is True
    assert r.is_tradable("dirt") is True


def test_unverified_vanilla_item_not_tradable():
    r = make_registry()
    assert r.runtime_item_id("iron_ingot") == "minecraft:iron_ingot"
    assert r.is_runtime_verified("iron_ingot") is False
    assert r.is_tradable("iron_ingot") is False


def test_create_mod_item_runtime_none():
    r = make_registry()
    for logical in ("iron_plate", "andesite_alloy", "brass_ingot", "gear", "shaft"):
        assert r.runtime_item_id(logical) is None
        assert r.is_runtime_verified(logical) is False
        assert r.is_tradable(logical) is False


def test_supply_ids_are_eight():
    r = make_registry()
    assert len(r.supply_ids()) == 8
    assert "bread" in r.supply_ids()
    assert "iron_ingot" not in r.supply_ids()


def test_unknown_logical_id_raises():
    r = make_registry()
    assert r.has("not_a_real_item") is False
    with pytest.raises(KeyError):
        r.get("not_a_real_item")


def test_economy_exposes_registry():
    eco = Economy()
    assert eco.registry is not None
    assert eco.registry.p0("iron_ingot") == 100
