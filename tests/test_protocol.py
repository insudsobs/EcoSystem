# -*- coding: utf-8 -*-
from protocol import (PROTOCOL_VERSION, KNOWN_REQUEST_TYPES,
                      MARKET_SUMMARY_REQ, QUOTE_BUY_REQ, QUOTE_SELL_REQ,
                      CONFIRM_QUOTE_REQ, CREATE_ORDER_REQ, CANCEL_ORDER_REQ,
                      MY_ORDERS_REQ, CLAIMS_REQ, CLAIM_REQ,
                      SERVER_AUTHORITATIVE_FIELDS)


def test_protocol_version():
    assert PROTOCOL_VERSION == 1


def test_all_request_types_known():
    for t in (MARKET_SUMMARY_REQ, QUOTE_BUY_REQ, QUOTE_SELL_REQ,
              CONFIRM_QUOTE_REQ, CREATE_ORDER_REQ, CANCEL_ORDER_REQ,
              MY_ORDERS_REQ, CLAIMS_REQ, CLAIM_REQ):
        assert t in KNOWN_REQUEST_TYPES


def test_server_authoritative_fields():
    assert "price" in SERVER_AUTHORITATIVE_FIELDS
    assert "marketVersion" in SERVER_AUTHORITATIVE_FIELDS
    assert "balance" in SERVER_AUTHORITATIVE_FIELDS
