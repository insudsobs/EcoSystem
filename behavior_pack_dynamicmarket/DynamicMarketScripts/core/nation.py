# -*- coding: utf-8 -*-
"""国家（Nation）实体与注册表。

国家是经济系统里的特殊实体：拥有领土（版图）、国库账户、税率。国库账户
对应 Economy 钱包中的 "nation:<id>" 账户，后续接国家税收时写入。
"""
from territory import Territory


class Nation(object):
    def __init__(self, nation_id, name, capital, territory, tax_rate_bps=0,
                 color=None):
        self.nation_id = nation_id
        self.name = name
        self.capital = capital          # (cx, cz)
        self.territory = territory      # Territory
        self.tax_rate_bps = tax_rate_bps  # 税率（bps），0 = 无税
        self.color = color              # 版图显示颜色标识（可选）

    def treasury_account(self):
        """国库账户名（对应 Economy 钱包）。"""
        return "nation:%s" % self.nation_id

    def contains(self, cx, cz):
        return self.territory.contains(cx, cz)

    def render(self):
        return self.territory.render(capital=self.capital)

    def snapshot(self):
        return {
            "nation_id": self.nation_id,
            "name": self.name,
            "capital": [self.capital[0], self.capital[1]],
            "tax_rate_bps": self.tax_rate_bps,
            "territory": self.territory.snapshot(),
        }

    @classmethod
    def from_snapshot(cls, data):
        capital = (data["capital"][0], data["capital"][1])
        territory = Territory.from_snapshot(data["territory"])
        return cls(data["nation_id"], data["name"], capital, territory,
                   data.get("tax_rate_bps", 0))


class NationRegistry(object):
    """国家注册表。"""

    def __init__(self):
        self._nations = {}

    def register(self, nation):
        self._nations[nation.nation_id] = nation
        return nation

    def get(self, nation_id):
        return self._nations.get(nation_id)

    def has(self, nation_id):
        return nation_id in self._nations

    def all(self):
        return [self._nations[k] for k in self._nations]

    def ids(self):
        return list(self._nations.keys())

    def nation_at(self, cx, cz):
        """返回包含 chunk (cx, cz) 的国家，无则 None。"""
        for nation in self._nations.values():
            if nation.contains(cx, cz):
                return nation
        return None

    def snapshot(self):
        return [n.snapshot() for n in self.all()]

    @classmethod
    def from_snapshot(cls, data):
        obj = cls()
        for d in data:
            obj.register(Nation.from_snapshot(d))
        return obj


def build_example_nation():
    """示例国家实例：Emberfall 王国，5x5 领土，中心 (0,0) 为首都。"""
    territory = Territory()
    for cx in range(-2, 3):
        for cz in range(-2, 3):
            territory.add_chunk(cx, cz)
    return Nation("emberfall", "Emberfall 王国", (0, 0), territory,
                  tax_rate_bps=500)


def build_example_registry():
    """示例国家注册表（两个相邻国家，展示版图显示）。"""
    reg = NationRegistry()
    reg.register(build_example_nation())

    # 第二个示例国：东侧 3x3 领土
    t2 = Territory()
    for cx in range(4, 7):
        for cz in range(-1, 2):
            t2.add_chunk(cx, cz)
    reg.register(Nation("frosthold", "Frosthold 公国", (5, 0), t2,
                        tax_rate_bps=300))
    return reg
