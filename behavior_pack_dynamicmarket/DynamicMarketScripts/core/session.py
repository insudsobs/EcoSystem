# -*- coding: utf-8 -*-
"""会话层（MarketSession）：组合 IdentityProvider + PersistentEconomyGate + Economy。

Runtime 外层负责把 runtime_player_id 解析为 account_id，并在长期交易前检查
gate。TradeService 只接受 account_id，不自行猜测 session/account 关系。

这是 PersistentEconomyGate 的实际接入点：未验证身份时，长期交易入口抛
IdentityNotVerified；只读入口（行情/报价）不受 gate 限制。
"""
from errors import IdentityNotVerified
from persistent_gate import PersistentEconomyGate


class MarketSession(object):
    def __init__(self, economy, identity_provider):
        self.economy = economy
        self.identity = identity_provider
        self.gate = PersistentEconomyGate(identity_provider)

    def _resolve_account(self, runtime_player_id, feature):
        """解析 account_id 并做 gate 检查。"""
        self.gate.require_persistence(feature)
        account_id = self.identity.resolve_account(runtime_player_id)
        if account_id is None:
            raise IdentityNotVerified(
                "cannot resolve long-term account for %r" % runtime_player_id)
        return account_id

    # ---- 长期交易入口（需 gate + account 解析） ----
    def place_sell_order(self, runtime_player_id, item_id, amount, unit_price,
                         expires_at=0, now=None):
        account_id = self._resolve_account(runtime_player_id, "sell_order_create")
        return self.economy.place_sell_order(account_id, item_id, amount,
                                             unit_price, expires_at, now)

    def cancel_order(self, runtime_player_id, order_id, now=None):
        account_id = self._resolve_account(runtime_player_id, "sell_order_create")
        return self.economy.cancel_order(account_id, order_id, now)

    def sell_to_system(self, runtime_player_id, item_id, quantity, now=None):
        account_id = self._resolve_account(runtime_player_id, "persistent_wallet")
        return self.economy.sell_to_system(account_id, item_id, quantity, now)

    def buy(self, runtime_player_id, item_id, quantity, quote_id, now=None):
        account_id = self._resolve_account(runtime_player_id, "persistent_wallet")
        return self.economy.buy(account_id, item_id, quantity, quote_id, now)

    def claim(self, runtime_player_id, claim_id, now=None):
        account_id = self._resolve_account(runtime_player_id, "claim_store")
        return self.economy.claim(account_id, claim_id, now)

    # ---- 只读入口（不受 gate 限制） ----
    def quote_item(self, item_id, quantity, side, now=None):
        return self.economy.quote_item(item_id, quantity, side, now)

    def market_summary(self, item_id, now=None):
        import market_view
        return market_view.market_summary(self.economy, item_id, now)

    def development_only(self):
        return self.gate.development_only()
