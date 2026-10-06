# Runtime Pending（真实运行时才能验证的能力）

以下能力在 20190712 SDK 文档中**找不到明确说明**，无法在 Mac 上验证，
必须在真实 Minecraft（中国版）运行时确认后才能宣称完成。在此之前一律标记
`TODO_RUNTIME` / `UNVERIFIED`，不得凭记忆补写。

## 1. 玩家身份

- [ ] 是否存在稳定玩家唯一标识（uid）。文档仅见实体 `id` 与 `name`。
- [ ] `playerId` 是否只代表当前实体（重进是否变化）。
- [ ] 玩家实体 `extraData` 是否跨重进长期保存（`EntityLoadScriptEvent` 证明
      实体 extraData 会持久化，但重进实体 id 是否稳定未明）。
- [ ] 玩家 `name` 是否可靠（重名/改名行为）。

**状态**：`PLAYER_IDENTITY_UNVERIFIED`。第一版钱包/长期挂单不绑定未验证 ID。

## 2. 背包（item 组件）

- [ ] 背包槽位范围 / 总数（文档未说明；`DropSlot=80` 是音效枚举）。
- [ ] `get_item_in_inventory_with_slot` 对空槽位的返回值。
- [ ] `addItems` 满包行为（是否部分成功 / 全部失败）。
- [ ] `addItems` 部分成功时如何获知实际写入数量。
- [ ] `offHandItem` / `carriedItem` 返回的 Item 字典完整字段（PARTIAL）。
- [ ] `auxValue` 语义与堆叠上限。

**状态**：`INVENTORY_SLOT_UNVERIFIED`。`MemoryInventory` 的堆叠/槽位模型是
可调假设，仅用于驱动核心逻辑的分支测试，不代表网易真实行为。

## 3. 持久化（extraData 组件）

- [ ] extraData 容量上限（`EXTRADATA_CAPACITY_UNVERIFIED`）。
- [ ] 写入后 `NeedsUpdate` 的落盘时机与 `ServerLevelSaveDataEvent` 的配合。
- [ ] 全局（levelId）extraData 与实体（entityId）extraData 的生命周期差异。
- [ ] 需要 chunking 才能存下的数据量阈值。

**状态**：接口已预留 chunking 扩展点，Phase 1 不实现 chunk system。

## 4. 时间

- [ ] 是否存在真实 Unix 时间 API。`time` 组件返回游戏帧（一天 24000 帧），
      非 Unix。`OnScriptTickServer` 1秒30次是唯一确认的时序信号。

**状态**：`Netease2019Scheduler` 用 tick 计数产生「秒级 pulse」，不保证与墙钟对齐。

## 5. 运行时事务

见 `RUNTIME_TRANSACTION_PLAN.md`。Phase 1 不声称 exactly-once 已解决。

## 6. 未找到的现代 API（已废弃，不得使用）

`mod.server.extraServerApi`、`CreateExtraData`、`AddTimer`、
`SpawnItemToPlayerInv`、`SetInvItemNum`、`GetPlayerAllItems`、现代 manifest
`script module` / `min_engine_version` / `dependencies`、稳定 uid API。

## 7. Phase 1.5 后的运行模式状态

- 当前 Mac 测试运行于 `CORE_ONLY`。
- identity 未验证 -> 最多 `RUNTIME_READONLY`（只读行情/价格查询/临时报价），
  identity 验证但 inventory/storage 未全验证 -> 最多 `RUNTIME_DEVELOPMENT`
  （session-only 交易，DEVELOPMENT_ONLY）。
- `RUNTIME_PRODUCTION` 要求 ProductionReadiness 全部关键项 verified：
  identity / inventorySlots / inventoryAdd / inventoryRemove /
  extraDataPersistence / runtimeItemIds / manifest。
- 在 MC Studio 实测前，不得宣称 Runtime 已验证、不得打开真实交易。
