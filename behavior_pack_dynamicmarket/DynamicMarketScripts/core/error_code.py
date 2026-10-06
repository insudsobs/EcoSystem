# -*- coding: utf-8 -*-
"""统一错误码（ErrorCode）。

UI / Runtime 只消费 error code + data，不解析英文异常字符串。
core exception 通过 error_code_of() 映射为稳定 error code。
"""
from errors import (IdentityNotVerified, InsufficientFunds, InsufficientStock,
                    InsufficientEscrow, ItemNotReceivable, QuoteExpired,
                    QuoteStale, QuoteNotFound, OrderNotFound, OrderNotOpen,
                    OrderExpired, ClaimNotFound, InvalidQuantity, InvalidPrice)

# 市场/商品
MARKET_DISABLED = "MARKET_DISABLED"
ITEM_NOT_TRADABLE = "ITEM_NOT_TRADABLE"

# 身份
IDENTITY_NOT_VERIFIED = "IDENTITY_NOT_VERIFIED"

# 资金/物品
INSUFFICIENT_BALANCE = "INSUFFICIENT_BALANCE"
INSUFFICIENT_ITEMS = "INSUFFICIENT_ITEMS"
INSUFFICIENT_LIQUIDITY = "INSUFFICIENT_LIQUIDITY"
SYSTEM_OUT_OF_STOCK = "SYSTEM_OUT_OF_STOCK"
SYSTEM_BUYBACK_CLOSED = "SYSTEM_BUYBACK_CLOSED"
INVENTORY_FULL = "INVENTORY_FULL"

# 报价
QUOTE_EXPIRED = "QUOTE_EXPIRED"
QUOTE_SUPERSEDED = "QUOTE_SUPERSEDED"
REQUOTE_REQUIRED = "REQUOTE_REQUIRED"

# 订单/领取
ORDER_NOT_FOUND = "ORDER_NOT_FOUND"
ORDER_NOT_OWNED = "ORDER_NOT_OWNED"
CLAIM_NOT_FOUND = "CLAIM_NOT_FOUND"

# 其他
INVALID_REQUEST = "INVALID_REQUEST"
RATE_LIMITED = "RATE_LIMITED"
INTERNAL_ERROR = "INTERNAL_ERROR"

# 基础映射（异常类型 -> code）。异常可显式携带 .code 覆盖。
_BASE_MAP = {
    IdentityNotVerified: IDENTITY_NOT_VERIFIED,
    InsufficientFunds: INSUFFICIENT_BALANCE,
    InsufficientStock: INSUFFICIENT_ITEMS,
    InsufficientEscrow: INSUFFICIENT_ITEMS,
    ItemNotReceivable: INVENTORY_FULL,
    QuoteExpired: QUOTE_EXPIRED,
    QuoteStale: QUOTE_SUPERSEDED,
    QuoteNotFound: REQUOTE_REQUIRED,
    OrderNotFound: ORDER_NOT_FOUND,
    OrderNotOpen: ORDER_NOT_FOUND,
    OrderExpired: ORDER_NOT_FOUND,
    ClaimNotFound: CLAIM_NOT_FOUND,
    InvalidQuantity: INVALID_REQUEST,
    InvalidPrice: INVALID_REQUEST,
}


def error_code_of(exc):
    """把 core exception 映射为 ErrorCode。优先用异常自带的 code。"""
    code = getattr(exc, "code", None)
    if code:
        return code
    for exc_type, c in _BASE_MAP.items():
        if isinstance(exc, exc_type):
            return c
    return INTERNAL_ERROR
