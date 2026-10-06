# 经济规格（DynamicMarket v0.1）

所有金额/库存/价格均为整数，百分比用 bps（万分比）表示，禁止 float。

## 1. 价格模型

系统理论价（纯整数）：

```
P = P0 * 3T / (2S + T)
```

- `P0`：正常基础价格；`T`：目标库存；`S`：当前 systemStock（≥0）。
- 性质：`S == T → P = P0`；`S → 0 → P → 3*P0`；`S → 3T → P → 3/7*P0`。
- ask（系统出售价）= P 加 spread；bid（系统收购价）= P 减 spread。
- `S > T` 时 bid 额外施加库存惩罚折扣；`S >= maxStock(=3T)` 停止收购。
- 默认 spread = 5%（500 bps），库存惩罚 = 5%（500 bps）。铁锭 P0=100，初始 S=T。

## 2. 商品（27 种）

- 基础保供 8 种：面包、熟马铃薯、圆石、石头、泥土、沙子、橡木原木、玻璃。
- 玩家生产 12 种：煤炭、木炭、铁锭、铜锭、金锭、红石粉、石英、青金石、
  小麦、马铃薯、胡萝卜、甘蔗。
- 加工材料 6 种：铁板、铜板、安山合金、黄铜锭、齿轮、传动轴。
- 贵重 1 种：钻石。

item identifier 全部为 `RUNTIME_ITEM_ID_PENDING` 占位，待真实组件 ID 回填。

## 3. 基础保供

- 仅 8 种保供物品有后台慢速补货，条件 `S < 30%T`。
- 补货速度约 `1%T/小时`，最多补到 `T`（不补到 maxStock）。
- 其他普通商品绝不自动生成。
- 触发由 Runtime Scheduler 按 tick 驱动（真实时间源 UNVERIFIED）。

## 4. 系统市场

- 玩家卖给系统：系统发行货币（`MoneySupply.issue`），系统库存增加。
- 玩家从系统购买：系统回收货币（`MoneySupply.destroy`），系统库存减少。
- 系统收购到 maxStock 为止（库存满拒绝，超量部分不收购）。

## 5. 玩家自由市场（v0.1 仅 SellOrder）

- 挂单：`itemId / amount / unitPrice`，物品即时从背包移入 Escrow。
- 排序：unitPrice 升序 → createdAt 升序 → orderId 升序。
- 成交：比较系统 ask 与最低玩家卖单，谁便宜买谁；同价优先玩家单。
- 大单允许 SYSTEM → PLAYER_ORDER → SYSTEM 动态穿越（系统价随库存下降而涨）。

## 6. 手续费

- 玩家订单成交手续费 1%（100 bps），卖家承担。
- 买家付 gross，卖家得 `gross - fee`，fee 从 MoneySupply 销毁。
- 余数按 seller 累积（非按订单），防止小额拆分逃费。

## 7. 货币（MoneySupply）

- `total = initial + issued - destroyed`，必须 ≥ 0。
- 卖给系统=发行、从系统买=回收、玩家间=转移、手续费=销毁。
- 禁用 `max(0, ...)` 兜底；出现负数即 `InvariantViolation`。
- 守恒不变量：`wallet.total_balance() == monetary.total()`。

## 8. 领取（Claim）

- 买家成交后物品进入 Claim（账本记录），随后 claim 领取到背包。
- 成交与发放分离，避免成交时背包满导致复杂回滚；claim 时背包满则失败，
  物品留在 Claim。

## 9. 行情历史

- 周期 5 分钟，记录 OHLC / VWAP / midPrice / marketPrice / systemStock /
  playerEscrowStock / buyVolume / sellVolume / turnover / tradeCount。
- VWAP = turnover // (buyVolume + sellVolume)，纯整数。
- 纯核心 `advance_to(now)` 驱动周期切换，Runtime 后由 OnScriptTickServer 驱动。

## 10. 状态与迁移

- `state_codec` 附加 `schemaVersion` + `checksum`；数据用 dict/list/int/str。
- 迁移路径预留，Phase 1 仅 schemaVersion 1。
