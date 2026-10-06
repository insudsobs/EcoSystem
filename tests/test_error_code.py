# -*- coding: utf-8 -*-
from errors import (IdentityNotVerified, InsufficientFunds, InsufficientStock,
                    InsufficientEscrow, ItemNotReceivable, QuoteExpired,
                    QuoteStale, OrderNotFound, ClaimNotFound)
from error_code import (error_code_of, IDENTITY_NOT_VERIFIED,
                        INSUFFICIENT_BALANCE, INSUFFICIENT_ITEMS,
                        INSUFFICIENT_LIQUIDITY, SYSTEM_BUYBACK_CLOSED,
                        INVENTORY_FULL, QUOTE_EXPIRED, QUOTE_SUPERSEDED,
                        ORDER_NOT_FOUND, CLAIM_NOT_FOUND, INTERNAL_ERROR)


def test_identity_not_verified():
    assert error_code_of(IdentityNotVerified("x")) == IDENTITY_NOT_VERIFIED


def test_insufficient_funds():
    assert error_code_of(InsufficientFunds("x")) == INSUFFICIENT_BALANCE


def test_insufficient_stock_default():
    assert error_code_of(InsufficientStock("x")) == INSUFFICIENT_ITEMS


def test_insufficient_stock_with_code():
    exc = InsufficientStock("x", code=SYSTEM_BUYBACK_CLOSED)
    assert error_code_of(exc) == SYSTEM_BUYBACK_CLOSED


def test_liquidity_code():
    exc = InsufficientStock("x", code=INSUFFICIENT_LIQUIDITY)
    assert error_code_of(exc) == INSUFFICIENT_LIQUIDITY


def test_inventory_full():
    assert error_code_of(ItemNotReceivable("x")) == INVENTORY_FULL


def test_quote_expired():
    assert error_code_of(QuoteExpired("x")) == QUOTE_EXPIRED


def test_quote_stale():
    assert error_code_of(QuoteStale("x")) == QUOTE_SUPERSEDED


def test_order_not_found():
    assert error_code_of(OrderNotFound("x")) == ORDER_NOT_FOUND


def test_claim_not_found():
    assert error_code_of(ClaimNotFound("x")) == CLAIM_NOT_FOUND


def test_unknown_maps_internal():
    assert error_code_of(ValueError("x")) == INTERNAL_ERROR
