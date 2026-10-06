# -*- coding: utf-8 -*-
"""生产就绪门禁（ProductionReadiness）。

任何关键项 False 则 can_enable_real_money_trade = False，
避免开发者因忘记一个 TODO 把半成品打开。
"""


class ProductionReadiness(object):
    def __init__(self, identity_verified=False, inventory_slots_verified=False,
                 inventory_add_verified=False, inventory_remove_verified=False,
                 extra_data_persistence_verified=False,
                 runtime_item_ids_verified=False, manifest_verified=False):
        self.identity_verified = identity_verified
        self.inventory_slots_verified = inventory_slots_verified
        self.inventory_add_verified = inventory_add_verified
        self.inventory_remove_verified = inventory_remove_verified
        self.extra_data_persistence_verified = extra_data_persistence_verified
        self.runtime_item_ids_verified = runtime_item_ids_verified
        self.manifest_verified = manifest_verified

    def can_enable_real_money_trade(self):
        return (self.identity_verified and
                self.inventory_slots_verified and
                self.inventory_add_verified and
                self.inventory_remove_verified and
                self.extra_data_persistence_verified and
                self.runtime_item_ids_verified and
                self.manifest_verified)

    def blockers(self):
        """返回未通过的关键项列表。"""
        out = []
        if not self.identity_verified:
            out.append("identityVerified")
        if not self.inventory_slots_verified:
            out.append("inventorySlotsVerified")
        if not self.inventory_add_verified:
            out.append("inventoryAddVerified")
        if not self.inventory_remove_verified:
            out.append("inventoryRemoveVerified")
        if not self.extra_data_persistence_verified:
            out.append("extraDataPersistenceVerified")
        if not self.runtime_item_ids_verified:
            out.append("runtimeItemIdsVerified")
        if not self.manifest_verified:
            out.append("manifestVerified")
        return out
