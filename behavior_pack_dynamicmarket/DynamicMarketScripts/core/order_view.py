# -*- coding: utf-8 -*-
"""订单数据合同（SellOrderView）。

客户端不需要看到 Escrow 内部结构。
"""


def sell_order_view(order):
    """把内部 SellOrder 转成 SellOrderView（纯 dict）。"""
    return {
        "orderId": order["order_id"],
        "itemId": order["item_id"],
        "originalAmount": order["amount"],
        "remainingAmount": order["remaining"],
        "unitPrice": order["unit_price"],
        "status": order["status"],
        "createdAt": order["created_at"],
        "expiresAt": order["expires_at"],
        "filledAmount": order["amount"] - order["remaining"],
    }
