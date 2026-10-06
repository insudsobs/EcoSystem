# -*- coding: utf-8 -*-
# RUNTIME_UNVERIFIED
# This module is based on 20190712 NetEase ModSDK documentation.
# It has not been executed inside MC Studio.
"""DynamicMarket 客户端 System（最小骨架）。

Phase 1 不做复杂 UI。仅注册 ClientSystem 占位。
"""
import client.extraClientApi as clientApi

ClientSystem = clientApi.GetClientSystemCls()


class DynamicMarketClient(ClientSystem):

    def __init__(self, namespace, systemName):
        super(DynamicMarketClient, self).__init__(namespace, systemName)

    def Destroy(self):
        pass
