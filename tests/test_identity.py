# -*- coding: utf-8 -*-
import pytest
from identity import PlayerIdentity, MemoryIdentityProvider
from persistent_gate import PersistentEconomyGate
from errors import IdentityNotVerified
from economy import Economy


def test_identity_can_hold_assets():
    assert PlayerIdentity("s1", "a1", "alice", True).can_hold_long_term_assets() is True
    assert PlayerIdentity("s2", None, "bob", True).can_hold_long_term_assets() is False
    assert PlayerIdentity("s3", "a3", "carol", False).can_hold_long_term_assets() is False


def test_two_sessions_same_account():
    provider = MemoryIdentityProvider()
    provider.bind("session_a", "account_1")
    provider.bind("session_b", "account_1")  # 两个 session 同一 account
    assert provider.resolve_account("session_a") == "account_1"
    assert provider.resolve_account("session_b") == "account_1"
    assert provider.resolve_session("session_b") == "session_b"


def test_unresolved_account_is_none():
    provider = MemoryIdentityProvider()
    assert provider.resolve_account("unknown_session") is None


def test_gate_blocks_unverified():
    provider = MemoryIdentityProvider(persistence_verified=False)
    gate = PersistentEconomyGate(provider)
    assert gate.persistence_verified() is False
    assert gate.development_only() is True
    with pytest.raises(IdentityNotVerified):
        gate.require_persistence("sell_order_create")


def test_gate_allows_verified():
    provider = MemoryIdentityProvider(persistence_verified=True)
    gate = PersistentEconomyGate(provider)
    gate.require_persistence("sell_order_create")  # 不抛


def test_gate_always_allows_read_and_quote():
    provider = MemoryIdentityProvider(persistence_verified=False)
    gate = PersistentEconomyGate(provider)
    assert gate.can_read_market() is True
    assert gate.can_quote() is True


def test_reconnect_order_belongs_to_same_account():
    # 模拟 Runtime 层：session -> account 转换后调用 core
    eco = Economy()
    provider = MemoryIdentityProvider()
    provider.bind("session_a", "account_1")
    provider.bind("session_b", "account_1")  # 重连新 session，同一 account

    eco.inventory.add_item("account_1", "iron_ingot", 100)
    eco.place_sell_order("account_1", "iron_ingot", 30, 100)

    # session_b（同一 account）能看到长期订单
    orders = eco.orderbook.open_orders("iron_ingot")
    assert len(orders) == 1
    assert orders[0]["seller"] == "account_1"


def test_unverified_account_rejected_for_long_term():
    provider = MemoryIdentityProvider()
    gate = PersistentEconomyGate(provider)
    # 无法解析 account -> 长期交易被拒绝
    with pytest.raises(IdentityNotVerified):
        gate.require_account(provider.resolve("unknown"), "sell_order_create")
