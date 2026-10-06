# -*- coding: utf-8 -*-
"""领域对象字段约定与构造辅助。

为兼容 Python 2.7 与网易 extraData（支持 dict/list/int/str，tuple 不支持），
领域对象一律用 dict 表示，字段以字符串 key 访问。此处只定义结构、常量与
构造辅助，不包含任何网易依赖。
"""

# ---------------------------------------------------------------------------
# 订单状态
# ---------------------------------------------------------------------------
ORDER_OPEN = "OPEN"              # 挂单中，可成交
ORDER_FILLED = "FILLED"          # 已全部成交
ORDER_CANCELLED = "CANCELLED"    # 已取消，托管已退回
ORDER_EXPIRED = "EXPIRED"        # 已过期，托管已退回

# 交易方向
SIDE_BUY = "BUY"
SIDE_SELL = "SELL"

# 成交来源
SOURCE_SYSTEM = "SYSTEM"         # 与系统市场成交
SOURCE_PLAYER_ORDER = "PLAYER_ORDER"  # 与玩家卖单成交

# 系统卖家标识（出现在 TradeFill.seller 中）
SYSTEM_SELLER = "SYSTEM"

# 领取条目状态
CLAIM_PENDING = "PENDING"
CLAIM_CLAIMED = "CLAIMED"


# ---------------------------------------------------------------------------
# SellOrder 字段:
#   order_id    int   单调递增
#   seller      str   卖家标识
#   item_id     str   物品标识
#   amount      int   挂单总量
#   remaining   int   剩余未成交量
#   unit_price  int   单价
#   created_at  int   创建时间(时钟秒)
#   expires_at  int   过期时间(时钟秒)，0 表示永不过期
#   status      str   OPEN/FILLED/CANCELLED/EXPIRED
# ---------------------------------------------------------------------------
def new_sell_order(order_id, seller, item_id, amount, unit_price,
                   created_at, expires_at=0):
    return {
        "order_id": order_id,
        "seller": seller,
        "item_id": item_id,
        "amount": amount,
        "remaining": amount,
        "unit_price": unit_price,
        "created_at": created_at,
        "expires_at": expires_at,
        "status": ORDER_OPEN,
    }


# ---------------------------------------------------------------------------
# Quote 字段:
#   quote_id         int   报价 id
#   item_id          str
#   side             str   BUY/SELL
#   quantity         int
#   unit_price       int   锁定单价
#   market_version   int   生成时的市场版本
#   created_at       int
#   expires_at       int   TTL 过期时间
# ---------------------------------------------------------------------------
def new_quote(quote_id, item_id, side, quantity, unit_price,
              market_version, created_at, expires_at):
    return {
        "quote_id": quote_id,
        "item_id": item_id,
        "side": side,
        "quantity": quantity,
        "unit_price": unit_price,
        "market_version": market_version,
        "created_at": created_at,
        "expires_at": expires_at,
    }


# ---------------------------------------------------------------------------
# TradeFill 字段（一次不可再分的成交段）:
#   fill_id     int
#   item_id     str
#   buyer       str   买家
#   seller      str   卖家，系统成交时为 SYSTEM
#   source      str   SYSTEM/PLAYER_ORDER
#   order_id    int   关联卖单 id，系统成交为 0
#   quantity    int
#   unit_price  int
#   gross       int   买家支付总额
#   fee         int   手续费(销毁)
#   net         int   卖家实得 = gross - fee
#   side        str   驱动方向 BUY/SELL（用于重建 History）
#   filled_at   int
# ---------------------------------------------------------------------------
def new_trade_fill(fill_id, item_id, buyer, seller, source, order_id,
                   quantity, unit_price, gross, fee, side, filled_at):
    return {
        "fill_id": fill_id,
        "item_id": item_id,
        "buyer": buyer,
        "seller": seller,
        "source": source,
        "order_id": order_id,
        "quantity": quantity,
        "unit_price": unit_price,
        "gross": gross,
        "fee": fee,
        "net": gross - fee,
        "side": side,
        "filled_at": filled_at,
    }


# ---------------------------------------------------------------------------
# Claim 字段（买家待领取物品）:
#   claim_id    int
#   player      str   买家
#   item_id     str
#   quantity    int
#   unit_price  int   成交单价(记录用)
#   created_at  int
#   status      str   PENDING/CLAIMED
# ---------------------------------------------------------------------------
def new_claim(claim_id, player, item_id, quantity, unit_price, created_at):
    return {
        "claim_id": claim_id,
        "player": player,
        "item_id": item_id,
        "quantity": quantity,
        "unit_price": unit_price,
        "created_at": created_at,
        "status": CLAIM_PENDING,
    }


# ---------------------------------------------------------------------------
# HistoryBar 字段（5 分钟 K 线）:
#   item_id             str
#   period_start        int   周期起点(对齐到 HISTORY_PERIOD_SECONDS)
#   open/high/low/close int
#   vwap                int   成交量加权均价 = turnover // volume（整数）
#   market_price        int   周期末系统理论价
#   mid_price           int   周期末 mid = (ask+bid)//2
#   system_stock        int   周期末系统库存
#   player_escrow_stock int   周期末玩家托管库存
#   buy_volume          int   周期内买单成交量
#   sell_volume         int   周期内卖单成交量
#   turnover            int   周期内成交额
#   trade_count         int   周期内成交笔数
# ---------------------------------------------------------------------------
def new_history_bar(item_id, period_start):
    return {
        "item_id": item_id,
        "period_start": period_start,
        "open": 0,
        "high": 0,
        "low": 0,
        "close": 0,
        "vwap": 0,
        "market_price": 0,
        "mid_price": 0,
        "system_stock": 0,
        "player_escrow_stock": 0,
        "buy_volume": 0,
        "sell_volume": 0,
        "turnover": 0,
        "trade_count": 0,
    }
