# -*- coding: utf-8 -*-
"""报价数据合同（QuoteView）。

客户端只展示，不能修改这些值回传作为权威数据。Confirm 只传 quoteId。
"""
from models import SIDE_BUY


def quote_view(quote, economy, now=None):
    """把内部 Quote 转成 QuoteView（纯 dict）。

    注意：QuoteView 的 gross/averagePrice/fee/net 是对当前市场的试算值，
    实际成交可能因滑点偏离；客户端不得回传这些值作为成交依据。
    """
    if now is None:
        now = economy.clock.now()
    item_id = quote["item_id"]
    market = economy.market
    side = quote["side"]

    if side == SIDE_BUY:
        unit_price = market.system_ask(item_id)
    else:
        unit_price = market.system_bid(item_id)

    quantity = quote["quantity"]
    gross = quantity * unit_price
    fee = 0
    if side == SIDE_BUY:
        # 买家订单成交时由卖家承担 1% 手续费，QuoteView 只做预估
        from config import FEE_BPS
        fee = gross * FEE_BPS // 10000
    net = gross - fee

    return {
        "quoteId": quote["quote_id"],
        "side": side,
        "itemId": item_id,
        "requestedAmount": quantity,
        "executableAmount": quantity,  # v0.1 不预估滑点，等于请求量
        "gross": gross,
        "averagePrice": unit_price,
        "fee": fee,
        "net": net,
        "beforeStock": market.system_stock(item_id),
        "afterStock": market.system_stock(item_id),  # 无副作用，前后一致
        "expiresAt": quote["expires_at"],
        "marketVersion": quote["market_version"],
        "replacementQuoteId": None,
        "requireReconfirm": False,
    }
