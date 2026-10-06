# -*- coding: utf-8 -*-
import pytest
from request_validator import RequestValidator, RequestValidationError
from item_registry import build_default_registry
from protocol import (PROTOCOL_VERSION, MARKET_SUMMARY_REQ, QUOTE_BUY_REQ,
                      CREATE_ORDER_REQ, CONFIRM_QUOTE_REQ)


def make_validator():
    return RequestValidator(build_default_registry(3),
                            max_order_amount=1000, max_string_length=128)


def req(msg_type, **fields):
    r = {"protocolVersion": PROTOCOL_VERSION, "type": msg_type}
    r.update(fields)
    return r


def test_rejects_non_dict():
    with pytest.raises(RequestValidationError):
        make_validator().validate("not a dict")


def test_rejects_bad_version():
    with pytest.raises(RequestValidationError):
        make_validator().validate(
            {"protocolVersion": 999, "type": MARKET_SUMMARY_REQ})


def test_rejects_unknown_type():
    with pytest.raises(RequestValidationError):
        make_validator().validate(req("HACK_TYPE"))


def test_valid_market_summary():
    v = make_validator().validate(req(MARKET_SUMMARY_REQ, itemId="iron_ingot"))
    assert v["itemId"] == "iron_ingot"


def test_rejects_non_str_item_id():
    with pytest.raises(RequestValidationError):
        make_validator().validate(req(MARKET_SUMMARY_REQ, itemId=123))


def test_rejects_unknown_item_id():
    with pytest.raises(RequestValidationError):
        make_validator().validate(req(MARKET_SUMMARY_REQ, itemId="hacker_item"))


def test_rejects_non_int_amount():
    with pytest.raises(RequestValidationError):
        make_validator().validate(req(QUOTE_BUY_REQ, itemId="iron_ingot", amount="10"))


def test_rejects_zero_amount():
    with pytest.raises(RequestValidationError):
        make_validator().validate(req(QUOTE_BUY_REQ, itemId="iron_ingot", amount=0))


def test_rejects_negative_amount():
    with pytest.raises(RequestValidationError):
        make_validator().validate(req(QUOTE_BUY_REQ, itemId="iron_ingot", amount=-5))


def test_rejects_bool_amount():
    # bool 是 int 子类，但协议不允许
    with pytest.raises(RequestValidationError):
        make_validator().validate(req(QUOTE_BUY_REQ, itemId="iron_ingot", amount=True))


def test_rejects_excess_amount():
    with pytest.raises(RequestValidationError):
        make_validator().validate(req(QUOTE_BUY_REQ, itemId="iron_ingot", amount=2000))


def test_rejects_server_authoritative_field():
    with pytest.raises(RequestValidationError):
        make_validator().validate(req(QUOTE_BUY_REQ, itemId="iron_ingot",
                                      amount=10, price=100))


def test_valid_create_order():
    v = make_validator().validate(req(CREATE_ORDER_REQ, itemId="iron_ingot",
                                      amount=10, unitPrice=100))
    assert v["amount"] == 10
    assert v["unitPrice"] == 100


def test_rejects_non_positive_unit_price():
    with pytest.raises(RequestValidationError):
        make_validator().validate(req(CREATE_ORDER_REQ, itemId="iron_ingot",
                                      amount=10, unitPrice=0))


def test_valid_confirm_quote():
    v = make_validator().validate(req(CONFIRM_QUOTE_REQ, quoteId=7))
    assert v["quoteId"] == 7


def test_unknown_extra_field_ignored():
    # 未知字段被忽略（不进入清理结果）
    v = make_validator().validate(req(MARKET_SUMMARY_REQ, itemId="iron_ingot",
                                      hackerField="evil"))
    assert "hackerField" not in v
