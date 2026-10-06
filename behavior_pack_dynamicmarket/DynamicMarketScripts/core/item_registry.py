# -*- coding: utf-8 -*-
"""商品注册表（ItemRegistry）。

经济核心（PriceEngine / Market / OrderBook / History）只认 logicalId；
只有 InventoryAdapter 负责 logicalId -> runtime item identifier 映射。
这样以后网易 item id 改动不需要修改经济核心。

runtimeItemId 为候选值；只有经 20190712 SDK / 实际 Runtime 确认后才
runtimeVerified = True。机械动力商品 runtimeItemId = None、runtimeVerified = False。
未验证 runtime id 的商品不得进入真实交易，但纯核心测试仍可使用 logicalId。
"""

MARKET_TYPE_SYSTEM = "system"      # 系统动态市场（有 systemStock）
MARKET_TYPE_FREE = "free_trade"    # 纯自由交易（未来，无系统库存）

CATEGORY_SUPPLY = "supply"
CATEGORY_PRODUCTION = "production"
CATEGORY_PROCESSED = "processed"
CATEGORY_PRECIOUS = "precious"


class ItemState(object):
    """单个商品的完整定义。"""

    def __init__(self, logical_id, display_name, p0, target_stock,
                 runtime_item_id, runtime_aux, market_type, enabled,
                 runtime_verified, is_supply, category):
        self.logical_id = logical_id
        self.display_name = display_name
        self.p0 = p0
        self.target_stock = target_stock
        self.runtime_item_id = runtime_item_id
        self.runtime_aux = runtime_aux
        self.market_type = market_type
        self.enabled = enabled
        self.runtime_verified = runtime_verified
        self.is_supply = is_supply
        self.category = category

    def is_tradable(self):
        """是否可进入真实交易（enabled 且 runtime id 已验证）。"""
        return self.enabled and self.runtime_verified and \
            self.runtime_item_id is not None


# (logical_id, display_name, p0, target_stock, runtime_item_id, runtime_aux,
#  market_type, enabled, runtime_verified, is_supply, category)
# runtime_item_id 为候选值；runtime_verified=False 表示待 SDK/实际 Runtime 确认。
_ITEM_DATA = [
    # ---- 基础保供 8 种 ----
    ("bread",         "面包",     20,  1000, "minecraft:bread",         0, MARKET_TYPE_SYSTEM, True, False, True,  CATEGORY_SUPPLY),
    ("cooked_potato", "熟马铃薯", 22,  1000, "minecraft:baked_potato",   0, MARKET_TYPE_SYSTEM, True, False, True,  CATEGORY_SUPPLY),
    ("cobblestone",   "圆石",     8,   2000, "minecraft:cobblestone",   0, MARKET_TYPE_SYSTEM, True, False, True,  CATEGORY_SUPPLY),
    ("stone",         "石头",     12,  1500, "minecraft:stone",         0, MARKET_TYPE_SYSTEM, True, False, True,  CATEGORY_SUPPLY),
    ("dirt",          "泥土",     4,   2000, "minecraft:dirt",          0, MARKET_TYPE_SYSTEM, True, True,  True,  CATEGORY_SUPPLY),
    ("sand",          "沙子",     6,   1500, "minecraft:sand",          0, MARKET_TYPE_SYSTEM, True, False, True,  CATEGORY_SUPPLY),
    ("oak_log",       "橡木原木", 10,  1500, "minecraft:log",           0, MARKET_TYPE_SYSTEM, True, False, True,  CATEGORY_SUPPLY),
    ("glass",         "玻璃",     25,  1000, "minecraft:glass",         0, MARKET_TYPE_SYSTEM, True, False, True,  CATEGORY_SUPPLY),

    # ---- 玩家生产 12 种 ----
    ("coal",          "煤炭",     25,  1500, "minecraft:coal",          0, MARKET_TYPE_SYSTEM, True, False, False, CATEGORY_PRODUCTION),
    ("charcoal",      "木炭",     28,  1200, "minecraft:coal",          1, MARKET_TYPE_SYSTEM, True, False, False, CATEGORY_PRODUCTION),
    ("iron_ingot",    "铁锭",     100, 800,  "minecraft:iron_ingot",   0, MARKET_TYPE_SYSTEM, True, False, False, CATEGORY_PRODUCTION),
    ("copper_ingot",  "铜锭",     85,  800,  "minecraft:copper_ingot", 0, MARKET_TYPE_SYSTEM, True, False, False, CATEGORY_PRODUCTION),
    ("gold_ingot",    "金锭",     280, 500,  "minecraft:gold_ingot",   0, MARKET_TYPE_SYSTEM, True, False, False, CATEGORY_PRODUCTION),
    ("redstone_dust", "红石粉",   70,  800,  "minecraft:redstone",     0, MARKET_TYPE_SYSTEM, True, False, False, CATEGORY_PRODUCTION),
    ("quartz",        "石英",     65,  800,  "minecraft:quartz",       0, MARKET_TYPE_SYSTEM, True, False, False, CATEGORY_PRODUCTION),
    ("lapis_lazuli",  "青金石",   55,  800,  "minecraft:dye",          4, MARKET_TYPE_SYSTEM, True, False, False, CATEGORY_PRODUCTION),
    ("wheat",         "小麦",     14,  1200, "minecraft:wheat",        0, MARKET_TYPE_SYSTEM, True, False, False, CATEGORY_PRODUCTION),
    ("potato",        "马铃薯",   16,  1000, "minecraft:potato",       0, MARKET_TYPE_SYSTEM, True, False, False, CATEGORY_PRODUCTION),
    ("carrot",        "胡萝卜",   18,  1000, "minecraft:carrot",       0, MARKET_TYPE_SYSTEM, True, False, False, CATEGORY_PRODUCTION),
    ("sugar_cane",    "甘蔗",     12,  1200, "minecraft:reeds",        0, MARKET_TYPE_SYSTEM, True, False, False, CATEGORY_PRODUCTION),

    # ---- 加工材料 6 种（机械动力，runtimeItemId 未知） ----
    ("iron_plate",    "铁板",     150, 600,  None, 0, MARKET_TYPE_SYSTEM, True, False, False, CATEGORY_PROCESSED),
    ("copper_plate",  "铜板",     130, 600,  None, 0, MARKET_TYPE_SYSTEM, True, False, False, CATEGORY_PROCESSED),
    ("andesite_alloy","安山合金", 190, 500,  None, 0, MARKET_TYPE_SYSTEM, True, False, False, CATEGORY_PROCESSED),
    ("brass_ingot",   "黄铜锭",   170, 500,  None, 0, MARKET_TYPE_SYSTEM, True, False, False, CATEGORY_PROCESSED),
    ("gear",          "齿轮",     240, 400,  None, 0, MARKET_TYPE_SYSTEM, True, False, False, CATEGORY_PROCESSED),
    ("shaft",         "传动轴",   210, 400,  None, 0, MARKET_TYPE_SYSTEM, True, False, False, CATEGORY_PROCESSED),

    # ---- 贵重 1 种 ----
    ("diamond",       "钻石",     1000, 200, "minecraft:diamond",      0, MARKET_TYPE_SYSTEM, True, False, False, CATEGORY_PRECIOUS),
]


class ItemRegistry(object):
    def __init__(self, items, max_stock_factor):
        self._items = {}
        for it in items:
            self._items[it.logical_id] = it
        self._max_stock_factor = max_stock_factor

    # ---- 查询 ----
    def get(self, logical_id):
        return self._items[logical_id]

    def has(self, logical_id):
        return logical_id in self._items

    def all(self):
        return [self._items[k] for k in self._items]

    def all_ids(self):
        return list(self._items.keys())

    def supply_ids(self):
        return [k for k, v in self._items.items() if v.is_supply]

    def enabled_ids(self):
        return [k for k, v in self._items.items() if v.enabled]

    def tradable_ids(self):
        return [k for k, v in self._items.items() if v.is_tradable()]

    # ---- 经济参数 ----
    def p0(self, logical_id):
        return self._items[logical_id].p0

    def target_stock(self, logical_id):
        return self._items[logical_id].target_stock

    def max_stock(self, logical_id):
        return self._items[logical_id].target_stock * self._max_stock_factor

    def is_supply(self, logical_id):
        return self._items[logical_id].is_supply

    # ---- runtime 标识 ----
    def runtime_item_id(self, logical_id):
        return self._items[logical_id].runtime_item_id

    def runtime_aux(self, logical_id):
        return self._items[logical_id].runtime_aux

    def is_runtime_verified(self, logical_id):
        return self._items[logical_id].runtime_verified

    def is_enabled(self, logical_id):
        return self._items[logical_id].enabled

    def is_tradable(self, logical_id):
        return self._items[logical_id].is_tradable()

    def display_name(self, logical_id):
        return self._items[logical_id].display_name


def build_default_registry(max_stock_factor):
    """构建默认 27 种商品的注册表。"""
    items = [ItemState(*row) for row in _ITEM_DATA]
    return ItemRegistry(items, max_stock_factor)
