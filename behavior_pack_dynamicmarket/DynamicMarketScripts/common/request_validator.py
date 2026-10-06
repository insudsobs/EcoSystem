# -*- coding: utf-8 -*-
"""请求输入严格校验（RequestValidator）。

纯 Python，不 import 网易。检查 dict 类型、protocolVersion、itemId 类型、
amount 为整数且 >0 且 <= maxOrderAmount、unitPrice >0、字符串最大长度、
未知 message type 等。客户端传来的 price/balance/stock/fee/tax/marketVersion
一律忽略（服务端自己算）。
"""
from protocol import (PROTOCOL_VERSION, KNOWN_REQUEST_TYPES,
                      FIELD_PROTOCOL_VERSION, FIELD_TYPE, FIELD_ITEM_ID,
                      FIELD_AMOUNT, FIELD_UNIT_PRICE, FIELD_QUOTE_ID,
                      FIELD_ORDER_ID, FIELD_CLAIM_ID, SERVER_AUTHORITATIVE_FIELDS,
                      MARKET_SUMMARY_REQ, QUOTE_BUY_REQ, QUOTE_SELL_REQ,
                      CONFIRM_QUOTE_REQ, CREATE_ORDER_REQ, CANCEL_ORDER_REQ,
                      MY_ORDERS_REQ, CLAIMS_REQ, CLAIM_REQ)


class RequestValidationError(ValueError):
    """请求校验失败。"""
    pass


class RequestValidator(object):
    def __init__(self, registry, max_order_amount, max_string_length):
        self._registry = registry
        self._max_order_amount = max_order_amount
        self._max_string_length = max_string_length

    def validate(self, request):
        """校验并返回清理后的 request（仅白名单字段）。"""
        if not isinstance(request, dict):
            raise RequestValidationError("request must be a dict")

        version = request.get(FIELD_PROTOCOL_VERSION)
        if isinstance(version, bool) or not isinstance(version, int) \
                or version != PROTOCOL_VERSION:
            raise RequestValidationError(
                "unsupported protocolVersion: %r" % (version,))

        msg_type = request.get(FIELD_TYPE)
        if msg_type not in KNOWN_REQUEST_TYPES:
            raise RequestValidationError("unknown message type: %r" % (msg_type,))

        cleaned = {
            FIELD_PROTOCOL_VERSION: PROTOCOL_VERSION,
            FIELD_TYPE: msg_type,
        }

        # 按消息类型校验字段
        if msg_type == MARKET_SUMMARY_REQ:
            cleaned[FIELD_ITEM_ID] = self._require_item_id(request)
        elif msg_type in (QUOTE_BUY_REQ, QUOTE_SELL_REQ):
            cleaned[FIELD_ITEM_ID] = self._require_item_id(request)
            cleaned[FIELD_AMOUNT] = self._require_amount(request)
        elif msg_type == CONFIRM_QUOTE_REQ:
            cleaned[FIELD_QUOTE_ID] = self._require_int(request, FIELD_QUOTE_ID, positive=True)
        elif msg_type == CREATE_ORDER_REQ:
            cleaned[FIELD_ITEM_ID] = self._require_item_id(request)
            cleaned[FIELD_AMOUNT] = self._require_amount(request)
            cleaned[FIELD_UNIT_PRICE] = self._require_int(request, FIELD_UNIT_PRICE, positive=True)
        elif msg_type == CANCEL_ORDER_REQ:
            cleaned[FIELD_ORDER_ID] = self._require_int(request, FIELD_ORDER_ID, positive=True)
        elif msg_type == MY_ORDERS_REQ:
            pass  # 无必需字段
        elif msg_type == CLAIMS_REQ:
            pass  # 无必需字段
        elif msg_type == CLAIM_REQ:
            cleaned[FIELD_CLAIM_ID] = self._require_int(request, FIELD_CLAIM_ID, positive=True)

        # 恶意字段（服务端权威字段）显式拒绝，其余未知字段忽略
        for field in SERVER_AUTHORITATIVE_FIELDS:
            if field in request:
                raise RequestValidationError(
                    "client must not set server-authoritative field: %r" % field)

        return cleaned

    # ---- 字段校验 ----
    def _require_item_id(self, request):
        item_id = request.get(FIELD_ITEM_ID)
        if not isinstance(item_id, str):
            raise RequestValidationError("itemId must be str")
        if len(item_id) > self._max_string_length:
            raise RequestValidationError("itemId too long")
        if not self._registry.has(item_id):
            raise RequestValidationError("unknown itemId: %r" % item_id)
        return item_id

    def _require_amount(self, request):
        amount = self._require_int(request, FIELD_AMOUNT, positive=True)
        if amount > self._max_order_amount:
            raise RequestValidationError(
                "amount %r exceeds max %r" % (amount, self._max_order_amount))
        return amount

    def _require_int(self, request, field, positive=False):
        value = request.get(field)
        # bool 是 int 子类，但协议不允许 bool
        if isinstance(value, bool) or not isinstance(value, int):
            raise RequestValidationError("%s must be int" % field)
        if positive and value <= 0:
            raise RequestValidationError("%s must be positive" % field)
        return value
