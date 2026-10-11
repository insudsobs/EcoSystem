# DynamicMarket 彻底重写（EcoRewrite）

网易《我的世界》中国版 Mod SDK（20190712）经济系统 DynamicMarket 的纯核心重写。

旧 EcoSystem 仓库已废弃，仅作功能需求参考；本仓库以
`《我的世界》中国版Mod SDK文档及工具20190712` 为唯一网易 API 依据，不搬用旧
网易 API 封装，不编造现代 ModSDK API。

## Mac Development Status

| 项 | 状态 |
|---|---|
| Pure Core | **VERIFIED**（纯 Python 测试覆盖） |
| NetEase 2019 API Mapping | **DOCUMENT VERIFIED**（见 docs/SDK_EVIDENCE.md） |
| Runtime Integration | **UNVERIFIED**（未在 MC Studio 运行） |
| Real Player Identity | **BLOCKED**（PLAYER_IDENTITY_UNVERIFIED，SDK 无稳定 uid） |
| Production Trading | **DISABLED**（ProductionReadiness 未达标） |

## 分层

- `behavior_pack_dynamicmarket/DynamicMarketScripts/core/`：纯经济核心，
  零网易依赖，Python 2.7 兼容 + Python 3 可测。
- `.../adapters/`：网易 20190712 适配器（接口 + `TODO_RUNTIME`，标注 RUNTIME_UNVERIFIED）。
- `.../server/ client/ common/`：网易 runtime 最小骨架（RUNTIME_UNVERIFIED）。
- `common/protocol.py`：协议常量（不 import 网易）。
- `common/request_validator.py`：请求输入严格校验。
- `docs/`：SDK 证据、架构、状态模型、经济规格、待验证清单、事务计划。
- `tests/`：纯 Python 3 测试。

## 核心模块速览

- `price_engine.py`：理论价 midPrice=P0*3T/(2S+T)，ask ceil / bid floor，
  连续库存惩罚，满仓停收购。
- `identity.py`：PlayerIdentity（session/account 分离）+ IdentityProvider。
- `persistent_gate.py`：PersistentEconomyGate，身份未验证禁用持久功能。
- `item_registry.py`：ItemRegistry，logicalId 与 runtime item id 分离。
- `market.py / orderbook.py / escrow.py / trade_service.py`：交易编排（plan/commit 原子）。
- `fill_store.py`：成交事实（AUTHORITATIVE），与 history（DERIVED）分离。
- `state_codec.py`：MarketState 序列化（schemaVersion/configVersion/savedAt/checksum）。
- `market_view.py / quote_view.py / order_view.py`：UI 数据合同。
- `error_code.py`：统一错误码。
- `runtime_mode.py / production_readiness.py`：运行模式与生产就绪门禁。
- `nation.py / territory.py`：国家实体与领土版图（chunk 坐标 + ASCII 版图显示），国库账户 `nation:<id>`。

## 运行测试（Mac）

```bash
python3 -m pytest tests/ -q
```

## Python 2.7 语法检查

```bash
# 首次：创建 venv 并安装 parso（仅用于语法检查，测试不需要）
python3 -m venv .venv && .venv/bin/pip install parso==0.7.1
# 检查进入 Minecraft 的脚本
.venv/bin/python tools/check_py2_syntax.py behavior_pack_dynamicmarket/DynamicMarketScripts
```

## 重要约束

- 无法在 Mac 上做真实 Minecraft Runtime 测试；Runtime 文件只做语法检查 +
  人工与 `docs/SDK_EVIDENCE.md` 核对。
- 玩家身份 `PLAYER_IDENTITY_UNVERIFIED`（SDK 无稳定 uid），禁止 username /
  hash(username) / 自造 UUID 当永久账号 ID。
- 背包槽位/满包行为、extraData 容量上限均为 UNVERIFIED，见
  `docs/RUNTIME_PENDING.md`。
