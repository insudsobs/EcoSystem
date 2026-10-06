# -*- coding: utf-8 -*-
"""网易 20190712 身份提供者（Netease2019IdentityProvider）。

This module is based on 20190712 NetEase ModSDK documentation.
It has not been executed inside MC Studio.

SDK 调查结论：AddServerPlayerEvent / DelServerPlayerEvent 仅回传实体 id，
无稳定 uid。因此：

  - resolve_session：可返回 runtime playerId（实体 id，会话级）。
  - resolve_account：返回 None（无法解析长期账户身份）。
  - is_persistence_verified：False。

在 MC Studio 实测确认稳定身份方案前，禁止用此身份进行长期真实交易。
"""
from core.identity import IdentityProvider


class Netease2019IdentityProvider(IdentityProvider):
    def __init__(self):
        pass

    def resolve_session(self, runtime_player_id):
        # 实体 id 作为会话身份
        return runtime_player_id

    def resolve_account(self, runtime_player_id):
        # 无稳定 uid，无法解析长期账户身份
        return None

    def is_persistence_verified(self):
        return False
