# 架构（三层）

DynamicMarket 分三层，core 完全不知道 Minecraft 存在。

```
DynamicMarketScripts/
├── core/       第一层：纯经济核心（零网易 import）
├── adapters/   第二层：把 core 的端口接到网易 runtime（TODO_RUNTIME）
├── server/     第三层：netease2019 runtime（server system 骨架）
├── client/     第三层：netease2019 runtime（client system 骨架）
├── common/     协议层 + 调度器（不 import 网易）
└── modMain.py  网易入口（TutorialMod 结构）
```

## 依赖方向（严格单向）

```
core  ←—— adapters  ←—— server / client
         common（协议常量/校验/调度器，不 import 网易）
```

## 核心模块

- `price_engine.py`：理论价 midPrice=P0*3T/(2S+T)，ask ceil / bid floor，
  连续库存惩罚，满仓停收购。
- `identity.py`：PlayerIdentity（session_id / account_id / display_name /
  persistence_verified）+ IdentityProvider。
- `persistent_gate.py`：PersistentEconomyGate，身份未验证禁用持久功能。
- `item_registry.py`：ItemRegistry，logicalId 与 runtime item id 分离
  （runtimeVerified 门禁）。
- `trade_service.py`：交易编排，buy 用 plan/commit 两阶段保证原子。
- `fill_store.py`：成交事实（AUTHORITATIVE）。
- `state_codec.py`：MarketState 序列化（schemaVersion/configVersion/savedAt/checksum）。
- `market_view.py / quote_view.py / order_view.py`：UI 数据合同。
- `error_code.py`：统一错误码。`runtime_mode.py / production_readiness.py`：运行模式与门禁。

## 端口（core 对外部能力的抽象）

| 端口 | core 接口 | Memory 实现（测试） | 网易实现 |
|---|---|---|---|
| 钱包 | `wallet.py:Wallet` | `MemoryWallet` | `adapters/netease2019_wallet.py` |
| 背包 | `inventory.py:Inventory` | `MemoryInventory` | `adapters/netease2019_inventory.py` |
| 存储 | `storage.py:Storage` | `MemoryStorage` | `adapters/netease2019_storage.py` |
| 时钟 | `clock.py:Clock` | `ManualClock` / `SystemClock` | `common/scheduler.py`（tick 驱动） |
| 身份 | `identity.py:IdentityProvider` | `MemoryIdentityProvider` | `adapters/netease2019_identity.py` |

## 玩家身份：PLAYER_IDENTITY_UNVERIFIED

SDK 无稳定 uid（AddServerPlayerEvent 仅回传实体 id）。core 长期资产使用
account_id，连接层使用 session_id，由 IdentityProvider 在 Runtime 外层转换。
禁止 username / hash(username) / 自造 UUID 当永久账号 ID。
详见 `identity.py` 与 `persistent_gate.py`。

## 商品标识分离

PriceEngine / Market / OrderBook / History 只认 logicalId；只有
InventoryAdapter 负责 logicalId -> runtime item identifier 映射。
runtimeItemId 未验证（runtimeVerified=False）的商品不得进入真实交易，
纯核心测试仍可使用 logicalId。详见 `item_registry.py`。

## 状态模型

AUTHORITATIVE（钱包/货币/库存/订单/托管/领取/手续费/成交/配置版本）必须持久化；
DERIVED（OHLC/VWAP/摘要/排序视图）可重建；EPHEMERAL（quotes/locks/session
映射/限流）不持久化。quotes v0.1 决定不保存。详见 `STATE_MODEL.md`。

## 序列化与持久化

- `state_codec.py`：JSON-compatible dict（禁止 pickle），canonical
  serialization + sha256 checksum，schemaVersion/configVersion/savedAt。
- 配置变化只改规则参数，不重置真实库存（每个 ItemState 记录 configVersion）。
- `storage.py` 接口预留 chunking 扩展点（extraData 容量上限未知）。

## 运行模式与门禁

`runtime_mode.py`（CORE_ONLY / RUNTIME_READONLY / RUNTIME_DEVELOPMENT /
RUNTIME_PRODUCTION）+ `production_readiness.py`（identity/inventory/
extraData/runtimeItemIds/manifest 全部 verified 才可真实交易）。
