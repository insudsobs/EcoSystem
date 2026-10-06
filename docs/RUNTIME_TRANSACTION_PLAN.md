# Runtime 事务计划（Phase 1 未实现，仅规划）

Mac 无法真正启动 Minecraft，因此 Phase 1 不做「已验证 WAL」。纯核心已用
plan/commit 两阶段保证内存事务原子；真实 Runtime 的跨系统事务边界如下，
**未验证前不得声称 exactly-once 已解决**。

## 危险操作（需真实运行时重点验证）

1. **BUY_SYSTEM 发物品**：买家扣钱 → 系统回收货币 → 系统库存减 → 物品发到
   玩家背包/Claim。若发放中途失败（背包满），钱已扣，需补偿或回滚。
2. **SELL_SYSTEM 删物品后发钱**：先删玩家背包物品，再发钱。删物品成功后发钱
   失败会丢物品；发钱成功后删物品失败会凭空造钱。
3. **ORDER_CREATE 背包转 Escrow**：挂单把物品从背包移出。移出后订单若未落盘，
   物品「消失」在 escrow。
4. **CLAIM 给物品后删 Claim**：给物品成功后删 Claim 失败 → 重复领取。

## 建议的真实事务策略（待 Runtime 验证后实现）

- 以 `ServerLevelSaveDataEvent` + `extraData` 为落盘点，先改内存账本，再落盘。
- 关键操作采用「账本先行（ledger-first）」：先记录意图（pending op），执行
  副作用，最后标记完成。重启后扫描未完成 op 做补偿。
- 网易 `addItems` / `invItemNum` 的部分成功行为未知（RUNTIME_PENDING），
  需要真实运行时先探明返回/可观察状态，再决定补偿策略。

## Phase 1 已提供的原子保证

- 纯核心 `buy`：plan（只读试算：报价有效性 + 余额 + 流动性）→ commit
  （全部应用或全部不应用），内存层面原子。
- `Economy.assert_invariants()` 校验货币守恒与库存非负，测试兜底。
