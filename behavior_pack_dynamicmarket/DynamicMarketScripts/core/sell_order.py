# -*- coding: utf-8 -*-
"""卖单辅助逻辑：排序键与状态转换。

排序规则（用户要求）：unitPrice 升序 -> createdAt 升序 -> orderId 升序。
同价时优先玩家订单（与系统价比较时由 market 层处理）。
"""
from models import (ORDER_OPEN, ORDER_FILLED, ORDER_CANCELLED, ORDER_EXPIRED)
from errors import OrderNotFound


def sort_key(order):
    """订单簿排序键。"""
    return (order["unit_price"], order["created_at"], order["order_id"])


def is_open(order):
    return order["status"] == ORDER_OPEN


def mark_filled(order):
    order["status"] = ORDER_FILLED
    return order


def mark_cancelled(order):
    order["status"] = ORDER_CANCELLED
    return order


def mark_expired(order):
    order["status"] = ORDER_EXPIRED
    return order


def require_open(order):
    """订单必须是 OPEN 状态，否则抛异常。"""
    if order is None:
        raise OrderNotFound("order not found")
    if order["status"] != ORDER_OPEN:
        raise OrderNotFound("order %r is not open (status=%s)"
                            % (order["order_id"], order["status"]))
    return order


def reduce_remaining(order, quantity):
    """成交后减少剩余量，减到 0 自动置 FILLED。"""
    order["remaining"] -= quantity
    if order["remaining"] == 0:
        mark_filled(order)
    return order
