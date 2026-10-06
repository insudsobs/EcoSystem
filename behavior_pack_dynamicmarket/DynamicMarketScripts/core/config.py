# -*- coding: utf-8 -*-
"""DynamicMarket 全局经济参数。

商品定义（logicalId / runtimeItemId / p0 / targetStock 等）见 item_registry.py。
本文件只保留全局参数。金额/库存/价格全部整数，百分比一律用 bps（万分比）。
"""

# 万分比换算：1% = 100 bps，5% = 500 bps
SPREAD_BPS = 500             # 系统 ask/bid 相对理论价的价差(5%)
FEE_BPS = 100                # 玩家订单成交手续费 1%，卖家承担

# 配置版本：P0/T/maxStock/marketType/item identifier 调整时递增。
# 保存状态时每个 ItemState 记录 configVersion；加载时配置变化只改规则参数，
# 不重置真实库存。
CONFIG_VERSION = 1

# 库存
DEFAULT_MAX_STOCK_FACTOR = 3  # maxStock = 3 * T

# 基础保供（仅 8 种，见 item_registry.is_supply）
SUPPLY_RESTOCK_THRESHOLD_PCT = 30   # S < 30%T 才启动慢速补货
SUPPLY_RESTOCK_RATE_PER_HOUR = 100  # 每小时补 T // 100（约 1% T），封顶 T

# 历史行情
HISTORY_PERIOD_SECONDS = 300        # 5 分钟

# 报价
QUOTE_TTL_SECONDS = 30              # 报价有效期

# 订单
DEFAULT_ORDER_TTL_SECONDS = 0       # 玩家卖单默认不过期(0)

# 请求输入上限
MAX_ORDER_AMOUNT = 1000000          # 单笔数量上限
MAX_STRING_LENGTH = 128             # 字符串字段最大长度
