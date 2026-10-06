# -*- coding: utf-8 -*-
# RUNTIME_UNVERIFIED
# This module is based on 20190712 NetEase ModSDK documentation.
# It has not been executed inside MC Studio.
"""网易 20190712 背包适配器（Netease2019InventoryAdapter）。

把网易 item 组件适配到 core.inventory.Inventory 接口。

已 VERIFIED（来源 3-1 Mod SDK文档.html，item组件 / SystemAPI）：
  - CreateComponent(playerId, "Minecraft", "item")   获取玩家物品组件
  - comp.invItemNum = [(slotPos, num)]               设置指定槽位数量
  - comp.addItems = [(itemName, count, auxValue, show,
                      {"to": "inventory", "playerId": pid})]   生成物品
  - GetCompData(comp, "item", "get_item_in_inventory_with_slot",
                playerId, slotPos)                    读取指定槽位物品
  - NeedsUpdate(comp)                                 组件更新

TODO_RUNTIME（文档未说明，必须真实运行时验证后才能宣称完成）：
  - 背包槽位范围 / 总数（文档无说明）
  - get_item_in_inventory_with_slot 对空槽位的返回值
  - addItems 满包 / 部分成功行为
  - offHandItem / carriedItem 返回的 Item 字典完整字段（PARTIAL）
  - auxValue 与堆叠上限语义

因此本类只定义接口形态，不写死未验证逻辑；方法体抛出
NotImplementedError 并注明 TODO_RUNTIME。
"""
from core.inventory import Inventory


class Netease2019InventoryAdapter(Inventory):
    def __init__(self, server_api):
        # server_api 为注入的 server.extraServerApi，避免硬 import 以便未来测试
        self._api = server_api

    # VERIFIED 用法骨架（注释引用，不直接执行）：
    #   comp = self._api.CreateComponent(playerId, "Minecraft", "item")
    #   slotData = self._api.GetCompData(
    #       comp, "item", "get_item_in_inventory_with_slot", playerId, slotPos)
    def count_item(self, player_id, item_id):
        # TODO_RUNTIME: 槽位范围与 item dict 字段未确认
        raise NotImplementedError("TODO_RUNTIME: count_item needs slot/item schema")

    def can_receive(self, player_id, item_id, amount):
        # TODO_RUNTIME: addItems 满包/部分成功行为未确认
        raise NotImplementedError("TODO_RUNTIME: can_receive needs full-bag behavior")

    def add_item(self, player_id, item_id, amount):
        # VERIFIED 骨架：comp.addItems = [...] + NeedsUpdate(comp)
        # TODO_RUNTIME: 满包/部分成功返回未确认，auxValue 未确认
        raise NotImplementedError("TODO_RUNTIME: add_item needs addItems semantics")

    def remove_item(self, player_id, item_id, amount):
        # VERIFIED 骨架：comp.invItemNum = [(slotPos, num)] + NeedsUpdate(comp)
        # TODO_RUNTIME: 槽位定位与部分扣除未确认
        raise NotImplementedError("TODO_RUNTIME: remove_item needs slot semantics")
