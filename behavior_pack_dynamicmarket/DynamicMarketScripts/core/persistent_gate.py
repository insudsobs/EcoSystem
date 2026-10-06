# -*- coding: utf-8 -*-
"""持久化经济功能门禁（PersistentEconomyGate）。

真实 Runtime 下，若 identity.persistence_verified == False，以下功能必须保持
DISABLED：持久钱包、SellOrder 创建、离线成交、ClaimStore、手续费长期归属、
长期历史 account attribution、国家税收。

始终允许：只读行情、系统价格查询、临时报价、开发调试模式下的 session-only
交易（必须明确标记 DEVELOPMENT_ONLY，不能默认发布）。
"""
from errors import IdentityNotVerified


class PersistentEconomyGate(object):
    # 需要长期持久身份的功能
    PERSISTENT_FEATURES = (
        "persistent_wallet",
        "sell_order_create",
        "offline_fill",
        "claim_store",
        "fee_attribution",
        "history_account_attribution",
        "national_tax",
    )

    def __init__(self, identity_provider):
        self._identity = identity_provider

    def persistence_verified(self):
        return self._identity.is_persistence_verified()

    def require_persistence(self, feature):
        """要求长期持久身份的功能入口守卫；未验证抛 IdentityNotVerified。"""
        if not self.persistence_verified():
            raise IdentityNotVerified(
                "feature %r requires verified persistence identity" % feature)

    def require_account(self, identity, feature):
        """要求该身份具备可长期持有的 account_id。"""
        if not identity.can_hold_long_term_assets():
            raise IdentityNotVerified(
                "feature %r requires a verified account id" % feature)

    def can_read_market(self):
        return True

    def can_quote(self):
        return True

    def development_only(self):
        """session-only 交易模式标记（DEVELOPMENT_ONLY）。"""
        return not self.persistence_verified()
