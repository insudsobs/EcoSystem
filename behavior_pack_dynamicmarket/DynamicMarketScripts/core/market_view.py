# -*- coding: utf-8 -*-
"""行情摘要数据合同（MarketSummary）。

返回纯 dict，UI 只消费这个，不自己算价格。所有数值为整数，
百分比变化用 bps（万分比）表示。
"""


def _last_trade_price(fill_store, item_id):
    fills = fill_store.get_by_item(item_id)
    if not fills:
        return None
    return fills[-1]["unit_price"]


def _mid_at(history, item_id, target_time):
    """找 target_time 之前最近的 bar 的 mid_price（含当前 bar）。"""
    best = None
    for b in history.bars(item_id):
        if b["period_start"] <= target_time:
            best = b
        else:
            break
    cur = history.current_bar(item_id)
    if cur is not None and cur["period_start"] <= target_time:
        best = cur
    return best


def _change_bps(history, item_id, current_mid, now, lookback_seconds):
    if lookback_seconds <= 0 or current_mid <= 0:
        return 0
    past = _mid_at(history, item_id, now - lookback_seconds)
    if past is None or past["mid_price"] <= 0:
        return 0
    return (current_mid - past["mid_price"]) * 10000 // past["mid_price"]


def _volume_turnover(fill_store, item_id, now, window_seconds):
    volume = 0
    turnover = 0
    for f in fill_store.get_range(now - window_seconds, now):
        volume += f["quantity"]
        turnover += f["gross"]
    return volume, turnover


def market_summary(economy, item_id, now=None):
    """某商品的行情摘要。"""
    if now is None:
        now = economy.clock.now()
    market = economy.market
    registry = economy.registry
    orderbook = economy.orderbook
    escrow = economy.escrow

    mid = market.mid_price(item_id)
    last = _last_trade_price(economy.fill_ledger, item_id)
    market_price = last if last is not None else mid

    best = orderbook.best_open(item_id)
    best_player_ask = best["unit_price"] if best is not None else None

    volume_24h, turnover_24h = _volume_turnover(economy.fill_ledger, item_id,
                                                now, 24 * 3600)

    return {
        "itemId": item_id,
        "displayName": registry.display_name(item_id),
        "marketPrice": market_price,
        "midPrice": mid,
        "systemAsk": market.system_ask(item_id),
        "systemBid": market.system_bid(item_id),
        "systemStock": market.system_stock(item_id),
        "targetStock": registry.target_stock(item_id),
        "maxStock": registry.max_stock(item_id),
        "playerEscrowStock": escrow.total_stock(item_id),
        "bestPlayerAsk": best_player_ask,
        "lastTradePrice": last,
        "change5mBps": _change_bps(economy.history, item_id, mid, now, 300),
        "change1hBps": _change_bps(economy.history, item_id, mid, now, 3600),
        "change24hBps": _change_bps(economy.history, item_id, mid, now, 86400),
        "volume24h": volume_24h,
        "turnover24h": turnover_24h,
        "systemBuyEnabled": market.can_buy_from_player(item_id),
        "systemSellEnabled": market.system_stock(item_id) > 0,
        "runtimeTradable": registry.is_tradable(item_id),
    }
