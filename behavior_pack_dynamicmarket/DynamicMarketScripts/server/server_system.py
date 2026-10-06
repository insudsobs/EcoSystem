# -*- coding: utf-8 -*-
# RUNTIME_UNVERIFIED
# This module is based on 20190712 NetEase ModSDK documentation.
# It has not been executed inside MC Studio.
"""DynamicMarket 服务端 System（最小骨架，仅已 VERIFIED 的 API）。

事件（3-1 已确认）：
  - AddServerPlayerEvent   回调仅 {id}，无稳定 uid -> PLAYER_IDENTITY_UNVERIFIED
  - DelServerPlayerEvent   回调仅 {id}
  - OnScriptTickServer     无参，1秒30次
"""
import server.extraServerApi as serverApi

ServerSystem = serverApi.GetServerSystemCls()


class DynamicMarketServer(ServerSystem):

    def __init__(self, namespace, systemName):
        super(DynamicMarketServer, self).__init__(namespace, systemName)
        self.ListenEvent()

    def ListenEvent(self):
        ns = serverApi.GetEngineNamespace()
        sys_name = serverApi.GetEngineSystemName()
        self.ListenForEvent(ns, sys_name, "AddServerPlayerEvent",
                            self, self.OnAddServerPlayer)
        self.ListenForEvent(ns, sys_name, "DelServerPlayerEvent",
                            self, self.OnDelServerPlayer)
        self.ListenForEvent(ns, sys_name, "OnScriptTickServer",
                            self, self.OnScriptTick)

    def UnListenEvent(self):
        ns = serverApi.GetEngineNamespace()
        sys_name = serverApi.GetEngineSystemName()
        self.UnListenForEvent(ns, sys_name, "AddServerPlayerEvent",
                              self, self.OnAddServerPlayer)
        self.UnListenForEvent(ns, sys_name, "DelServerPlayerEvent",
                              self, self.OnDelServerPlayer)
        self.UnListenForEvent(ns, sys_name, "OnScriptTickServer",
                              self, self.OnScriptTick)

    def OnAddServerPlayer(self, args):
        # args 仅含 "id"（实体 id）。无稳定 uid，长期钱包/挂单不能建立在
        # 未验证的实体 id 上（PLAYER_IDENTITY_UNVERIFIED）。
        pass

    def OnDelServerPlayer(self, args):
        pass

    def OnScriptTick(self, args):
        # 1秒30次 tick。周期任务交给 Netease2019Scheduler 计数驱动，
        # 不要每 tick 执行全部经济逻辑。
        pass

    def Destroy(self):
        self.UnListenEvent()
