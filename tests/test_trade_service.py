# -*- coding: utf-8 -*-
import pytest
from economy import Economy
from models import SIDE_BUY, SIDE_SELL, SOURCE_SYSTEM, SOURCE_PLAYER_ORDER
from errors import (InsufficientFunds, InsufficientStock, OrderNotFound,
                    QuoteStale, QuoteExpired, ItemNotReceivable)
import config as cfg


def fund(eco, player, item_id="diamond", amount=400):
    """通过卖给系统换取货币（守恒）。"""
    eco.inventory.add_item(player, item_id, amount)
    return eco.sell_to_system(player, item_id, amount)


def give_item(eco, player, item_id, amount):
    eco.inventory.add_item(player, item_id, amount)


# ---------------------------------------------------------------------------
# 系统买 / 系统卖
# ---------------------------------------------------------------------------
def test_sell_to_system_issues_money():
    eco = Economy()
    give_item(eco, "alice", "iron_ingot", 100)
    stock_before = eco.market.system_stock("iron_ingot")
    gross = eco.sell_to_system("alice", "iron_ingot", 50)
    assert gross > 0
    assert eco.wallet.balance("alice") == gross
    assert eco.market.system_stock("iron_ingot") == stock_before + 50
    assert eco.inventory.count_item("alice", "iron_ingot") == 50
    eco.assert_invariants()


def test_buy_from_system_goes_to_claim():
    eco = Economy()
    fund(eco, "bob")
    balance = eco.wallet.balance("bob")
    quote = eco.quote_item("iron_ingot", 10, SIDE_BUY)
    fills = eco.buy("bob", "iron_ingot", 10, quote["quote_id"])
    assert all(f["source"] == SOURCE_SYSTEM for f in fills)
    # 钱减少，物品进 Claim
    assert eco.wallet.balance("bob") < balance
    pending = eco.claim_store.pending("bob")
    assert sum(c["quantity"] for c in pending) == 10
    eco.assert_invariants()


def test_claim_delivers_to_inventory():
    eco = Economy()
    fund(eco, "bob")
    quote = eco.quote_item("iron_ingot", 10, SIDE_BUY)
    eco.buy("bob", "iron_ingot", 10, quote["quote_id"])
    claims = eco.claim_store.pending("bob")
    assert len(claims) == 1
    eco.claim("bob", claims[0]["claim_id"])
    assert eco.inventory.count_item("bob", "iron_ingot") == 10
    assert eco.claim_store.pending("bob") == []


def test_sell_to_system_stops_at_max_stock():
    eco = Economy()
    max_stock = eco.registry.max_stock("diamond")  # 600，初始 200
    give_item(eco, "alice", "diamond", 500)
    # 一次性卖超量，系统只收到 maxStock
    eco.sell_to_system("alice", "diamond", 500)
    assert eco.market.system_stock("diamond") == max_stock
    assert eco.inventory.count_item("alice", "diamond") == 100  # 未收部分保留
    # 再次卖应拒绝
    with pytest.raises(InsufficientStock):
        eco.sell_to_system("alice", "diamond", 1)


# ---------------------------------------------------------------------------
# 挂单 / Escrow / 取消 / 过期
# ---------------------------------------------------------------------------
def test_place_order_moves_to_escrow():
    eco = Economy()
    give_item(eco, "alice", "iron_ingot", 100)
    order = eco.place_sell_order("alice", "iron_ingot", 30, 100)
    assert order["status"] == "OPEN"
    assert eco.inventory.count_item("alice", "iron_ingot") == 70
    assert eco.escrow.total_stock("iron_ingot") == 30


def test_cancel_order_refunds():
    eco = Economy()
    give_item(eco, "alice", "iron_ingot", 100)
    order = eco.place_sell_order("alice", "iron_ingot", 30, 100)
    eco.cancel_order("alice", order["order_id"])
    assert eco.inventory.count_item("alice", "iron_ingot") == 100
    assert eco.escrow.total_stock("iron_ingot") == 0
    assert eco.orderbook.get(order["order_id"])["status"] == "CANCELLED"


def test_cancel_wrong_player_raises():
    eco = Economy()
    give_item(eco, "alice", "iron_ingot", 100)
    order = eco.place_sell_order("alice", "iron_ingot", 30, 100)
    with pytest.raises(OrderNotFound):
        eco.cancel_order("mallory", order["order_id"])


def test_expire_orders_refunds():
    eco = Economy()
    give_item(eco, "alice", "iron_ingot", 100)
    order = eco.place_sell_order("alice", "iron_ingot", 30, 100, expires_at=100)
    expired = eco.expire_orders(now=100)
    assert len(expired) == 1
    assert eco.inventory.count_item("alice", "iron_ingot") == 100
    assert eco.escrow.total_stock("iron_ingot") == 0


# ---------------------------------------------------------------------------
# 撮合：价格/时间/同价优先/动态穿越
# ---------------------------------------------------------------------------
def test_player_order_fills_when_cheaper():
    eco = Economy()
    fund(eco, "bob")
    give_item(eco, "alice", "iron_ingot", 100)
    eco.place_sell_order("alice", "iron_ingot", 30, 100)  # < 系统 ask(105)
    quote = eco.quote_item("iron_ingot", 20, SIDE_BUY)
    fills = eco.buy("bob", "iron_ingot", 20, quote["quote_id"])
    assert all(f["source"] == SOURCE_PLAYER_ORDER for f in fills)
    assert all(f["seller"] == "alice" for f in fills)
    # 卖家得到 gross - fee
    gross = sum(f["gross"] for f in fills)
    fee = sum(f["fee"] for f in fills)
    assert eco.wallet.balance("alice") == gross - fee
    eco.assert_invariants()


def test_price_priority():
    eco = Economy()
    fund(eco, "bob")
    give_item(eco, "alice", "iron_ingot", 100)
    give_item(eco, "carol", "iron_ingot", 100)
    eco.place_sell_order("alice", "iron_ingot", 10, 100)
    eco.place_sell_order("carol", "iron_ingot", 10, 90)
    quote = eco.quote_item("iron_ingot", 10, SIDE_BUY)
    fills = eco.buy("bob", "iron_ingot", 10, quote["quote_id"])
    # 优先买 carol 的 90
    assert fills[0]["seller"] == "carol"
    assert fills[0]["unit_price"] == 90


def test_player_priority_on_equal_price():
    eco = Economy()
    fund(eco, "bob")
    ask = eco.market.system_ask("iron_ingot")
    give_item(eco, "alice", "iron_ingot", 100)
    eco.place_sell_order("alice", "iron_ingot", 30, ask)  # 与系统同价
    quote = eco.quote_item("iron_ingot", 10, SIDE_BUY)
    fills = eco.buy("bob", "iron_ingot", 10, quote["quote_id"])
    assert fills[0]["source"] == SOURCE_PLAYER_ORDER


def test_dynamic_cross_system_and_player():
    eco = Economy()
    fund(eco, "bob")
    give_item(eco, "alice", "iron_ingot", 100)
    eco.place_sell_order("alice", "iron_ingot", 10, 95)  # 低于系统 ask
    quote = eco.quote_item("iron_ingot", 30, SIDE_BUY)
    fills = eco.buy("bob", "iron_ingot", 30, quote["quote_id"])
    # 先玩家 10@95，再系统 20（系统价随库存下降上涨，可能分段）
    assert fills[0]["source"] == SOURCE_PLAYER_ORDER
    assert fills[0]["quantity"] == 10
    system_fills = fills[1:]
    assert all(f["source"] == SOURCE_SYSTEM for f in system_fills)
    assert sum(f["quantity"] for f in system_fills) == 20
    # 系统价随库存下降单调不降（动态穿越的正确表现）
    for i in range(len(system_fills) - 1):
        assert system_fills[i]["unit_price"] <= system_fills[i + 1]["unit_price"]
    eco.assert_invariants()


# ---------------------------------------------------------------------------
# 手续费：拆单不可逃避
# ---------------------------------------------------------------------------
def test_fee_split_equivalent():
    eco = Economy()
    fund(eco, "bob")
    give_item(eco, "alice", "iron_ingot", 100)
    eco.place_sell_order("alice", "iron_ingot", 50, 100)

    # 单笔买 150 -> 手续费按 gross 一次性算
    quote1 = eco.quote_item("iron_ingot", 50, SIDE_BUY)
    fills1 = eco.buy("bob", "iron_ingot", 50, quote1["quote_id"])
    fee_single = sum(f["fee"] for f in fills1)

    # 拆成 3 笔各买一部分（需要重新挂单）
    eco2 = Economy()
    fund(eco2, "bob")
    give_item(eco2, "alice", "iron_ingot", 100)
    eco2.place_sell_order("alice", "iron_ingot", 50, 100)
    fee_split = 0
    for _ in range(5):
        q = eco2.quote_item("iron_ingot", 10, SIDE_BUY)
        fee_split += sum(f["fee"] for f in eco2.buy("bob", "iron_ingot", 10, q["quote_id"]))
    # 拆分不逃费：总手续费不低于单笔（余数累积保证）
    assert fee_split >= fee_single


# ---------------------------------------------------------------------------
# 报价：无副作用 / TTL / marketVersion / 数量 replacement
# ---------------------------------------------------------------------------
def test_quote_no_side_effect():
    eco = Economy()
    before = eco.market.version()
    stock = eco.market.system_stock("iron_ingot")
    eco.quote_item("iron_ingot", 10, SIDE_BUY)
    assert eco.market.version() == before
    assert eco.market.system_stock("iron_ingot") == stock


def test_quote_expires():
    eco = Economy()
    fund(eco, "bob")
    quote = eco.quote_item("iron_ingot", 10, SIDE_BUY, now=0)
    with pytest.raises(QuoteExpired):
        eco.buy("bob", "iron_ingot", 10, quote["quote_id"], now=cfg.QUOTE_TTL_SECONDS)


def test_quote_stale_on_version_change():
    eco = Economy()
    fund(eco, "bob")
    quote = eco.quote_item("iron_ingot", 10, SIDE_BUY)
    # 市场变化（挂单）导致 version 递增
    give_item(eco, "alice", "iron_ingot", 100)
    eco.place_sell_order("alice", "iron_ingot", 5, 100)
    with pytest.raises(QuoteStale):
        eco.buy("bob", "iron_ingot", 10, quote["quote_id"])


def test_quote_quantity_mismatch_requires_replacement():
    eco = Economy()
    fund(eco, "bob")
    quote = eco.quote_item("iron_ingot", 10, SIDE_BUY)
    with pytest.raises(QuoteStale):
        eco.buy("bob", "iron_ingot", 20, quote["quote_id"])


def test_double_confirm_rejected():
    eco = Economy()
    fund(eco, "bob")
    quote = eco.quote_item("iron_ingot", 10, SIDE_BUY)
    eco.buy("bob", "iron_ingot", 10, quote["quote_id"])
    # 已成交后市场 version 变化，重复 confirm 应被拒
    with pytest.raises(QuoteStale):
        eco.buy("bob", "iron_ingot", 10, quote["quote_id"])


# ---------------------------------------------------------------------------
# 原子性 / rollback
# ---------------------------------------------------------------------------
def test_buy_rollback_on_insufficient_funds():
    eco = Economy()
    give_item(eco, "alice", "iron_ingot", 100)
    eco.place_sell_order("alice", "iron_ingot", 10, 90)
    quote = eco.quote_item("iron_ingot", 10, SIDE_BUY)
    with pytest.raises(InsufficientFunds):
        eco.buy("bob", "iron_ingot", 10, quote["quote_id"])  # bob 没钱
    # 回滚后 alice 挂单与托管不变
    assert eco.escrow.total_stock("iron_ingot") == 10
    assert eco.wallet.balance("bob") == 0
    eco.assert_invariants()


def test_buy_rollback_on_liquidity():
    eco = Economy()
    fund(eco, "bob", "diamond", 400)
    quote = eco.quote_item("iron_ingot", 900, SIDE_BUY)  # 系统仅 800，无玩家单
    with pytest.raises(InsufficientStock):
        eco.buy("bob", "iron_ingot", 900, quote["quote_id"])
    eco.assert_invariants()


def test_multi_seller_atomic():
    eco = Economy()
    fund(eco, "bob")
    for seller in ("alice", "carol", "dave"):
        give_item(eco, seller, "iron_ingot", 100)
        eco.place_sell_order(seller, "iron_ingot", 10, 90)
    quote = eco.quote_item("iron_ingot", 25, SIDE_BUY)
    fills = eco.buy("bob", "iron_ingot", 25, quote["quote_id"])
    sellers = {f["seller"] for f in fills}
    assert sellers == {"alice", "carol", "dave"}
    assert sum(f["quantity"] for f in fills) == 25
    eco.assert_invariants()


def test_cheap_player_order_zero_fee():
    # 单价 1 的便宜玩家单，gross=1，fee=0，不应因 monetary.destroy(0) 崩溃
    eco = Economy()
    fund(eco, "bob")
    give_item(eco, "alice", "iron_ingot", 100)
    eco.place_sell_order("alice", "iron_ingot", 1, 1)
    quote = eco.quote_item("iron_ingot", 1, SIDE_BUY)
    fills = eco.buy("bob", "iron_ingot", 1, quote["quote_id"])
    assert fills[0]["fee"] == 0
    eco.assert_invariants()


def test_system_player_system_cross():
    # 系统价随库存下降上涨，中途超过玩家单 -> SYSTEM -> PLAYER -> SYSTEM 穿越
    eco = Economy()
    fund(eco, "bob", "diamond", 400)
    give_item(eco, "alice", "iron_ingot", 100)
    eco.place_sell_order("alice", "iron_ingot", 10, 110)  # 介于系统 ask 初始与上涨后之间
    quote = eco.quote_item("iron_ingot", 200, SIDE_BUY)
    fills = eco.buy("bob", "iron_ingot", 200, quote["quote_id"])
    sources = [f["source"] for f in fills]
    assert SOURCE_PLAYER_ORDER in sources
    player_idx = sources.index(SOURCE_PLAYER_ORDER)
    assert SOURCE_SYSTEM in sources[:player_idx]   # 前面有系统成交
    assert SOURCE_SYSTEM in sources[player_idx + 1:]  # 后面也有系统成交
    eco.assert_invariants()
