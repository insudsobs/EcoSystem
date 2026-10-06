# -*- coding: utf-8 -*-
# RUNTIME_UNVERIFIED
# This module is based on 20190712 NetEase ModSDK documentation.
# It has not been executed inside MC Studio.
"""网易 20190712 钱包持久化适配器（Netease2019Wallet）。

钱包余额的持久化依赖 extraData 组件（见 netease2019_storage.py），
Phase 1 不实现真实写入，仅定义接口形态。

重要：玩家身份 UNVERIFIED（AddServerPlayerEvent 仅回传实体 id，无稳定 uid），
因此本适配器不能宣称提供「全服稳定钱包」，调用方需自行处理
PLAYER_IDENTITY_UNVERIFIED 风险。
"""
from core.wallet import Wallet


class Netease2019Wallet(Wallet):
    def __init__(self, storage):
        # storage 为 Netease2019ExtraDataStorage 实例
        self._storage = storage
        self._cache = {}

    def balance(self, player_id):
        # TODO_RUNTIME: 从 extraData 读取并缓存
        raise NotImplementedError("TODO_RUNTIME: balance needs extraData read")

    def credit(self, player_id, amount):
        raise NotImplementedError("TODO_RUNTIME: credit needs extraData write")

    def debit(self, player_id, amount):
        raise NotImplementedError("TODO_RUNTIME: debit needs extraData write")

    def total_balance(self):
        raise NotImplementedError("TODO_RUNTIME: total_balance needs full scan")
