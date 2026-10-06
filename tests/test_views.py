# -*- coding: utf-8 -*-
from economy import Economy
from market_view import market_summary
from quote_view import quote_view
from order_view import sell_order_view
from models import SIDE_BUY

SUMMARY_FIELDS = ("itemId", "displayName", "marketPrice", "midPrice", "systemAsk",
                  "systemBid", "systemStock", "targetStock", "maxStock",
                  "playerEscrowStock", "bestPlayerAsk", "lastTradePrice",
                  "change5mBps", "change1hBps", "change24hBps", "volume24h",
                  "turnover24h", "systemBuyEnabled", "systemSellEnabled",
                  "runtimeTradable")

QUOTE_FIELDS = ("quoteId", "side", "itemId", "requestedAmount",
                "executableAmount", "gross", "averagePrice", "fee", "net",
                "beforeStock", "afterStock", "expiresAt", "marketVersion",
                "replacementQuoteId", "requireReconfirm")

ORDER_FIELDS = ("orderId", "itemId", "originalAmount", "remainingAmount",
                "unitPrice", "status", "createdAt", "expiresAt", "filledAmount")


def test_market_summary_fields():
    eco = Economy()
    s = market_summary(eco, "iron_ingot")
    for key in SUMMARY_FIELDS:
        assert key in s, "missing %s" % key


def test_market_summary_runtime_tradable():
    eco = Economy()
    assert market_summary(eco, "iron_ingot")["runtimeTradable"] is False
    assert market_summary(eco, "dirt")["runtimeTradable"] is True


def test_market_summary_best_player_ask():
    eco = Economy()
    assert market_summary(eco, "iron_ingot")["bestPlayerAsk"] is None
    eco.inventory.add_item("alice", "iron_ingot", 100)
    eco.place_sell_order("alice", "iron_ingot", 10, 90)
    assert market_summary(eco, "iron_ingot")["bestPlayerAsk"] == 90


def test_quote_view_fields():
    eco = Economy()
    quote = eco.quote_item("iron_ingot", 10, SIDE_BUY)
    v = quote_view(quote, eco)
    for key in QUOTE_FIELDS:
        assert key in v, "missing %s" % key
    assert v["requestedAmount"] == 10


def test_sell_order_view_fields():
    eco = Economy()
    eco.inventory.add_item("alice", "iron_ingot", 100)
    order = eco.place_sell_order("alice", "iron_ingot", 30, 100)
    v = sell_order_view(order)
    for key in ORDER_FIELDS:
        assert key in v, "missing %s" % key
    assert v["originalAmount"] == 30
    assert v["remainingAmount"] == 30
    assert v["filledAmount"] == 0
