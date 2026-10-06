# SDK Evidence（20190712 网易 Mod SDK 证据表）

唯一依据：`《我的世界》中国版Mod SDK文档及工具20190712/`（已解压）。
来源文件简称：

- `3-1` = `3 Mod SDK/3-1 Mod SDK文档.html`
- `3-4` = `3 Mod SDK/3-4 UI API.html`
- `TutorialMod` = `6 示例/6-1DemoMod/TutorialMod/`
- `LobbyGoodDemo` = `6 示例/6-1DemoMod/LobbyGoodDemo/`

Status 仅允许：`VERIFIED`（文档明确）、`PARTIAL`（文档有但不完整）、`NOT_FOUND`（文档未出现）。

> 本表是所有网易 API 引用的唯一来源。任何进入 Mod 脚本的网易 API 必须先出现于此。

---

## 1. 入口与绑定

| Capability | Exact API | Side | Source | Section | Example | Status |
|---|---|---|---|---|---|---|
| 绑定类 | `from common.mod import Mod` | both | TutorialMod | modMain.py | `@Mod.Binding(name="TutorialMod", version="0.0.1")` | VERIFIED |
| 服务端初始化 | `@Mod.InitServer()` | server | TutorialMod | modMain.py | 注册 System | VERIFIED |
| 客户端初始化 | `@Mod.InitClient()` | client | TutorialMod | modMain.py | 注册 System | VERIFIED |
| 服务端析构 | `@Mod.DestroyServer()` | server | TutorialMod | modMain.py | 反注册 | VERIFIED |
| 客户端析构 | `@Mod.DestroyClient()` | client | TutorialMod | modMain.py | 反注册 | VERIFIED |
| API 模块 | `import server.extraServerApi as serverApi` | server | TutorialMod | modMain.py | — | VERIFIED |
| API 模块 | `import client.extraClientApi as clientApi` | client | TutorialMod | modMain.py | — | VERIFIED |

---

## 2. 注册与基类（模块级）

| Capability | Exact API | Side | Source | Status |
|---|---|---|---|---|
| 注册系统 | `serverApi.RegisterSystem(namespace, systemName, clsPath)` | server | 3-1 / TutorialMod | VERIFIED |
| 注册系统 | `clientApi.RegisterSystem(namespace, systemName, clsPath)` | client | 3-1 / TutorialMod | VERIFIED |
| 注册组件 | `serverApi.RegisterComponent(namespace, name, clsPath)` | server | 3-1 / LobbyGoodDemo | VERIFIED |
| 系统基类 | `serverApi.GetServerSystemCls()` | server | 3-1 / TutorialMod | VERIFIED |
| 系统基类 | `clientApi.GetClientSystemCls()` | client | 3-1 / TutorialMod | VERIFIED |
| 组件基类 | `serverApi.GetComponentCls()` | server | 3-1 / LobbyGoodDemo | VERIFIED |
| 引擎命名空间 | `GetEngineNamespace()` | both | 3-1 / TutorialMod | VERIFIED |
| 引擎系统名 | `GetEngineSystemName()` | both | 3-1 / TutorialMod | VERIFIED |
| levelId | `GetLevelId()` | server | 3-1 / TutorialMod | VERIFIED |
| 本地玩家 id | `clientApi.GetLocalPlayerId()` | client | 3-1 / LobbyGoodDemo | VERIFIED |
| 枚举 | `GetMinecraftEnum()` | both | 3-1 / LobbyGoodDemo | VERIFIED |

---

## 3. SystemAPI（System 类实例方法）

来源 3-1「SystemAPI」节，服务器/客户端 system 均可使用。

| Capability | Exact API | Status |
|---|---|---|
| 创建组件 | `CreateComponent(entityId, nameSpace, name)` | VERIFIED |
| 获取组件 | `GetComponent(entityId, nameSpace, name)` | VERIFIED |
| 删除组件 | `DestroyComponent(entityId, nameSpace, name)` | VERIFIED |
| 组件数据 | `GetCompData(comp, moduleName, funcName, *args)` | VERIFIED |
| 组件更新 | `NeedsUpdate(comp)`（System 方法）；`serverApi.NeedsUpdate(comp)`（模块级，LobbyGoodDemo 佐证） | VERIFIED |
| 临时实体 | `CreateTempEntity()` | VERIFIED |
| 创建实体 | `CreateEntity(tempEntity)` | VERIFIED |
| 销毁实体 | `DestroyEntity(entityId)` | VERIFIED |
| 定义事件 | `DefineEvent(eventName)` | VERIFIED |
| 反定义事件 | `UnDefineEvent(eventName)` | VERIFIED |
| 事件数据 | `CreateEventData()`（返回 dict，可嵌套 dict/list/基本类型，不支持 tuple） | VERIFIED |
| 监听事件 | `ListenForEvent(namespace, systemName, eventName, instance, func)` | VERIFIED |
| 反监听 | `UnListenForEvent(namespace, systemName, eventName, instance, func)` | VERIFIED |
| 本地广播 | `BroadcastEvent(eventName, eventData)` | VERIFIED |
| 广播所有客户端 | `BroadcastToAllClient(eventName, eventData)`（仅服务器） | VERIFIED |
| 发指定客户端 | `NotifyToClient(targetId, eventName, eventData)`（仅服务器，targetId 为玩家 id） | VERIFIED |
| 发服务器 | `NotifyToServer(eventName, eventData)`（仅客户端） | VERIFIED |

---

## 4. 服务端事件

| Capability | 回调参数 | Source | Status |
|---|---|---|---|
| `AddServerPlayerEvent`（玩家加入） | 仅 `id: str 玩家id` | 3-1 | VERIFIED |
| `DelServerPlayerEvent`（删除玩家） | 仅 `id: str 玩家id` | 3-1 | VERIFIED |
| `ServerChatEvent`（聊天） | `username: str`, `playerId: str`, `message: str` | 3-1 / TutorialMod | VERIFIED |
| `OnScriptTickServer` | 无参；备注「1秒30次tick」 | 3-1 | VERIFIED |
| `ServerLevelSaveDataEvent` | 无参 | 3-1 | VERIFIED |
| `EntityLoadScriptEvent` | `id: str 实体id`；备注「只有使用过 exDataComp 的实体才有」 | 3-1 | VERIFIED |
| `ServerLevelCreateBeginEvent` / `ServerLevelCreateFinishedEvent` | 无参 | 3-1 | VERIFIED |

## 5. 客户端事件

| Capability | 回调参数 | Source | Status |
|---|---|---|---|
| `AddPlayerEvent`（玩家加入） | `id: str 实体id` | 3-1 / LobbyGoodDemo | VERIFIED |
| `UiInitFinished`（UI 框架初始化完成，可创建 UI） | 无参 | 3-1 | VERIFIED |
| `OnScriptTickClient` | 无参；1秒30次 | 3-1 | VERIFIED |

---

## 6. 组件（Minecraft 命名空间）

| Capability | 组件名 | 关键字段/用法 | Source | Status |
|---|---|---|---|---|
| 物品 | `item` | `comp.addItems=[(itemName,count,auxValue,show,{"to":"inventory","playerId":pid})]`；`comp.addItemDicts=[(itemDict,{...})]`；`comp.invItemNum=[(slotPos,num)]`；`comp.invItemExchange=[(s1,s2)]`；`comp.offHandItem`；`comp.carriedItem`；`comp.slotId`；`comp.registerItems` | 3-1 / TutorialMod | VERIFIED |
| 读指定槽位 | `item` | `GetCompData(comp,"item","get_item_in_inventory_with_slot",playerId,slotPos)` | 3-1 | VERIFIED |
| 持久化 | `extraData` | `CreateComponent(entityId/levelId,"Minecraft","extraData")`；`comp.extraData.key=value`；存 leveldb；支持基本类型（tuple 不支持）；entityId 挂实体 / levelId 挂全局 | 3-1 | VERIFIED |
| 玩家名 | `name` | `CreateComponent(playerId,"Minecraft","name")` → `comp.name`（str） | 3-1 | VERIFIED |
| 名片 | `name` | `CreateComponent(entityId,"Minecraft","name")` → `comp.showName`（bool） | 3-1 | VERIFIED |
| 时间 | `time` | `CreateComponent(levelId,"Minecraft","time")` → `comp.time`（int，游戏帧，一天 24000 帧，非 Unix） | 3-1 | VERIFIED |

---

## 7. UI API

| Capability | Exact API | Source | Status |
|---|---|---|---|
| 注册 UI | `RegisterUI(namespace, uiKey, clsPath, uiNameSpace)` | 3-1 / 3-4 | VERIFIED |
| 创建 UI | `CreateUI(namespace, uiKey, createParams)` | 3-1 / 3-4 | VERIFIED |
| 获取 UI | `GetUI(namespace, uiKey)` | 3-1 / 3-4 | VERIFIED |
| 隐藏 HUD | `HideHudGUI(isHide)` | 3-1 | VERIFIED |

（Phase 1 不实现 UI，仅记录 API 存在。）

---

## 8. manifest

| Capability | 结构 | Source | Status |
|---|---|---|---|
| Behavior Pack | `format_version:1` + `header{description,name,uuid,version}` + `modules[{type:"data"}]` | TutorialMod manifest.json | VERIFIED |
| Resource Pack | 同上，`modules[{type:"resources"}]` | TutorialMod manifest.json | VERIFIED |

---

## 9. 关键负面结论（旧假设被推翻）

| 假设 | 结论 | 证据 |
|---|---|---|
| 稳定 uid | **不存在**。`AddServerPlayerEvent`/`DelServerPlayerEvent` 仅回传 `id`（实体 id） | 3-1 事件参数表 |
| `mod.server.extraServerApi` | **NOT_FOUND**（正确是 `server.extraServerApi`） | 全文档 |
| `CreateExtraData` | **NOT_FOUND**（正确是 `CreateComponent(id,"Minecraft","extraData")`） | 3-1 |
| `AddTimer` | **NOT_FOUND**（周期任务用 `OnScriptTickServer` 自建 Scheduler） | 3-1 |
| `SpawnItemToPlayerInv` | **NOT_FOUND**（正确是 item 组件 `addItems`） | 3-1 |
| `SetInvItemNum` | **NOT_FOUND**（正确是 item 组件 `invItemNum`） | 3-1 |
| `GetPlayerAllItems` | **NOT_FOUND**（正确是 `get_item_in_inventory_with_slot` 逐槽读） | 3-1 |
| 现代 manifest `script module` / `min_engine_version` / `dependencies` | **NOT_FOUND** | TutorialMod manifest |
| 真实 Unix 时间 API | **NOT_FOUND**（`time` 组件是游戏帧时间） | 3-1 |

---

## 10. 未完全确认（PARTIAL / UNVERIFIED）

| Capability | Status | 说明 |
|---|---|---|
| `offHandItem` / `carriedItem` 返回 Item 字典完整字段 | PARTIAL | 文档仅写「Item字典」，字段未逐项列出；可从 `addItemDicts` 的 itemDict 反推 itemId/count/auxValue/enchantData/customTips/extraId/modId/modItemId |
| 玩家实体 extraData 跨重进持久 + playerId 跨重进稳定 | PARTIAL | `EntityLoadScriptEvent` 证明实体 extraData 会持久化，但「玩家重进是否同一实体 id」文档未明 |
| 背包槽位范围/总数 | NOT_FOUND | 文档未说明；`DropSlot=80` 是音效枚举，非背包槽位 |
| addItems 满包/部分成功行为 | NOT_FOUND | 文档未说明 |
| 堆叠上限 / auxValue 语义 | NOT_FOUND | 文档未说明 |
| extraData 容量上限 | NOT_FOUND | 文档未说明 |
| get_item_in_inventory_with_slot 空槽位返回值 | NOT_FOUND | 文档未说明 |
