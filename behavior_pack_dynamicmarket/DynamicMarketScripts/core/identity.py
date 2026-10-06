# -*- coding: utf-8 -*-
"""玩家身份抽象。

core 不知道网易 playerId。身份分两层：

  - session_id：当前在线实体/会话身份（对应网易 runtime playerId）。
  - account_id：可安全用于长期资产的身份（钱包余额、长期挂单、Claim、手续费归属）。

约束（不可违反）：

  - persistence_verified == False 时，禁止使用该身份进行需要长期账户的真实交易。
  - 禁止用 username 直接当永久账号 ID。
  - 禁止 hash(username) 当永久账号 ID。
  - 禁止自行给第一次进入的人生成 UUID 然后假装以后一定能找回。
  - account_id 不允许凭空构造：只有真实 Runtime 实测确认后才允许持久化绑定。
"""


class PlayerIdentity(object):
    """一个玩家的身份快照。"""

    def __init__(self, session_id, account_id, display_name, persistence_verified):
        self.session_id = session_id
        self.account_id = account_id
        self.display_name = display_name
        self.persistence_verified = persistence_verified

    def can_hold_long_term_assets(self):
        """是否有可安全用于长期资产的 account_id。"""
        return self.persistence_verified and self.account_id is not None


class IdentityProvider(object):
    """身份解析接口。Runtime 外层负责把 runtime_player_id 转成 PlayerIdentity。

    core 的 TradeService 只接受 account_id（长期身份），不自行猜测
    session 与 account 的关系。
    """

    def resolve_session(self, runtime_player_id):
        raise NotImplementedError

    def resolve_account(self, runtime_player_id):
        raise NotImplementedError

    def resolve_display_name(self, runtime_player_id):
        return self.resolve_session(runtime_player_id)

    def is_persistence_verified(self):
        raise NotImplementedError

    def resolve(self, runtime_player_id):
        """解析完整身份。account_id 为 None 表示无法解析长期身份。"""
        return PlayerIdentity(
            session_id=self.resolve_session(runtime_player_id),
            account_id=self.resolve_account(runtime_player_id),
            display_name=self.resolve_display_name(runtime_player_id),
            persistence_verified=self.is_persistence_verified(),
        )


class MemoryIdentityProvider(IdentityProvider):
    """内存身份提供者：可提供稳定 account_id，用于纯核心测试。

    - 未 bind 的 runtime_player_id 解析 account_id 为 None（模拟无法解析）。
    - 多个不同 session 可显式 bind 到同一个 account_id（重连归属测试）。
    """

    def __init__(self, persistence_verified=True):
        self._accounts = {}     # runtime_player_id -> account_id
        self._names = {}        # runtime_player_id -> display_name
        self._counter = 0
        self._persistence_verified = persistence_verified

    def bind(self, runtime_player_id, account_id=None, display_name=None):
        """绑定（或生成）稳定 account_id。返回 account_id。"""
        if account_id is None:
            self._counter += 1
            account_id = "account_%d" % self._counter
        self._accounts[runtime_player_id] = account_id
        if display_name is not None:
            self._names[runtime_player_id] = display_name
        return account_id

    def resolve_session(self, runtime_player_id):
        return runtime_player_id

    def resolve_account(self, runtime_player_id):
        return self._accounts.get(runtime_player_id)

    def resolve_display_name(self, runtime_player_id):
        return self._names.get(runtime_player_id, runtime_player_id)

    def is_persistence_verified(self):
        return self._persistence_verified
