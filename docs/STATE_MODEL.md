# 状态模型（STATE_MODEL）

经济状态分三类：AUTHORITATIVE / DERIVED / EPHEMERAL。

## AUTHORITATIVE（权威状态，必须持久化，不可由其他状态重建）

| 状态 | 存储 | 说明 |
|---|---|---|
| wallet balances | `money.wallets` | 账户余额 |
| monetary ledger | `money.supply` | initial/issued/destroyed |
| systemStock | `market.stock` | 每种商品系统库存（含 configVersion） |
| marketVersion | `market.version` | 市场版本，报价失效依据 |
| orders | `orders` | 卖单（含 remaining/status） |
| escrow | `escrow` | 挂单托管 |
| claims | `claims` | 待领取物品 |
| fee accumulator | `fees` | 手续费余数（按 seller） |
| fills | `fills` | 成交事实 |
| item config version | `market.stock[*].configVersion` | 商品配置版本 |

## DERIVED（派生状态，可从 AUTHORITATIVE 重建）

- OHLC / VWAP（可由 fills 重建）
- market summary（由 market + orderbook 即时计算）
- price cache（由 price_engine 即时计算）
- sorted order views（由 orders 即时排序）

`history` 为 DERIVED，可选保存（加速启动），也可不保存由 fills 重建。

## EPHEMERAL（临时状态，不持久化，重启失效）

- **quotes**：v0.1 决定**不保存**，服务器重启后所有 Quote 失效（更简单更安全）。
- locks（内存锁）
- session mapping（session_id -> account_id 映射，由 IdentityProvider 重建）
- rate-limit state
- temporary UI state

## 序列化约束

- 编码格式：JSON-compatible dict（dict/list/int/str/bool/null），禁止 pickle。
- 禁止直接序列化 class instance（必须转纯 dict）。
- canonical serialization + sha256 checksum。
- Python 2.7 与 Python 3 结果语义一致。
- MarketState 顶层字段：`configVersion / money / market / orders / escrow /
  claims / fees / fills / history(optional)`；`state_codec` 包装层加
  `schemaVersion / savedAt / checksum`。
