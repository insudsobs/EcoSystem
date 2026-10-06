# -*- coding: utf-8 -*-
# RUNTIME_UNVERIFIED
# This module is based on 20190712 NetEase ModSDK documentation.
# It has not been executed inside MC Studio.
"""网易 20190712 持久化适配器（Netease2019ExtraDataStorage）。

把网易 extraData 组件适配到 core.storage.Storage 接口。

已 VERIFIED（来源 3-1，exData/extraData 组件）：
  - CreateComponent(levelId, "Minecraft", "extraData")   全局数据
  - CreateComponent(entityId, "Minecraft", "extraData")  实体数据
  - comp.extraData.key = value                           写入
  - 数据存 leveldb；支持 python 基本数据类型（tuple 不支持）
  - NeedsUpdate(comp)

UNVERIFIED（见 docs/RUNTIME_PENDING.md）：
  - extraData 容量上限（EXTRADATA_CAPACITY_UNVERIFIED）
  - 玩家实体 extraData 是否跨重进持久 + playerId 是否跨重进稳定（PARTIAL：
    EntityLoadScriptEvent 证明实体 extraData 会持久化，但玩家重进是否
    同一实体 id 文档未明）

Phase 1 只定义接口形态，方法体抛 NotImplementedError 并注明 TODO_RUNTIME。
"""
from core.storage import Storage


class Netease2019ExtraDataStorage(Storage):
    def __init__(self, server_api, level_id):
        self._api = server_api
        self._level_id = level_id

    # VERIFIED 用法骨架：
    #   comp = self._api.CreateComponent(self._level_id, "Minecraft", "extraData")
    #   comp.extraData.dynamicMarket = blob
    #   self._api.NeedsUpdate(comp)
    def load(self):
        # TODO_RUNTIME: 读取全局 extraData 的返回值形态需真实运行时确认
        raise NotImplementedError("TODO_RUNTIME: load needs extraData read semantics")

    def save(self, blob):
        # TODO_RUNTIME: 写入与 NeedsUpdate 时机需真实运行时确认
        raise NotImplementedError("TODO_RUNTIME: save needs extraData write semantics")
