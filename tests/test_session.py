# -*- coding: utf-8 -*-
import pytest
from economy import Economy
from identity import MemoryIdentityProvider
from session import MarketSession
from errors import IdentityNotVerified


def test_unverified_identity_blocks_long_term():
    eco = Economy()
    provider = MemoryIdentityProvider(persistence_verified=False)
    session = MarketSession(eco, provider)
    with pytest.raises(IdentityNotVerified):
        session.place_sell_order("session_1", "iron_ingot", 10, 100)


def test_unverified_identity_allows_read():
    eco = Economy()
    provider = MemoryIdentityProvider(persistence_verified=False)
    session = MarketSession(eco, provider)
    summary = session.market_summary("iron_ingot")
    assert summary["itemId"] == "iron_ingot"


def test_unresolved_account_blocks():
    eco = Economy()
    provider = MemoryIdentityProvider(persistence_verified=True)
    session = MarketSession(eco, provider)
    with pytest.raises(IdentityNotVerified):
        session.place_sell_order("unknown_session", "iron_ingot", 10, 100)


def test_verified_session_trades():
    eco = Economy()
    provider = MemoryIdentityProvider(persistence_verified=True)
    provider.bind("session_1", "account_1")
    session = MarketSession(eco, provider)
    eco.inventory.add_item("account_1", "iron_ingot", 100)
    order = session.place_sell_order("session_1", "iron_ingot", 30, 100)
    assert order["seller"] == "account_1"


def test_two_sessions_same_account_via_session():
    eco = Economy()
    provider = MemoryIdentityProvider()
    provider.bind("session_a", "account_1")
    provider.bind("session_b", "account_1")
    session = MarketSession(eco, provider)
    eco.inventory.add_item("account_1", "iron_ingot", 100)
    session.place_sell_order("session_a", "iron_ingot", 30, 100)
    orders = eco.orderbook.open_orders("iron_ingot")
    assert orders[0]["seller"] == "account_1"


def test_trade_service_rejects_none_account():
    eco = Economy()
    with pytest.raises(IdentityNotVerified):
        eco.trade.sell_to_system(None, "iron_ingot", 10)
