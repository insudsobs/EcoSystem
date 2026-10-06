# -*- coding: utf-8 -*-
# RUNTIME_UNVERIFIED
# This module is based on 20190712 NetEase ModSDK documentation.
# It has not been executed inside MC Studio.
# DynamicMarket 入口。结构与官方 TutorialMod 一致（20190712 SDK）。
from common.mod import Mod
import server.extraServerApi as serverApi
import client.extraClientApi as clientApi


@Mod.Binding(name="DynamicMarket", version="0.0.1")
class DynamicMarketMod(object):

    def __init__(self):
        pass

    @Mod.InitServer()
    def InitServer(self):
        serverApi.RegisterSystem(
            "DynamicMarket", "DynamicMarketServer",
            "DynamicMarketScripts.server.server_system.DynamicMarketServer")

    @Mod.DestroyServer()
    def DestroyServer(self):
        pass

    @Mod.InitClient()
    def InitClient(self):
        clientApi.RegisterSystem(
            "DynamicMarket", "DynamicMarketClient",
            "DynamicMarketScripts.client.client_system.DynamicMarketClient")

    @Mod.DestroyClient()
    def DestroyClient(self):
        pass
