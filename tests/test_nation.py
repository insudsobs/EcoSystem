# -*- coding: utf-8 -*-
from nation import (Nation, NationRegistry, build_example_nation,
                    build_example_registry)
from territory import Territory


def test_nation_treasury_account():
    n = build_example_nation()
    assert n.treasury_account() == "nation:emberfall"


def test_nation_render():
    n = build_example_nation()
    rendered = n.render()
    assert "@" in rendered          # 首都在版图中标记
    assert len(rendered.split("\n")) == 5  # 5x5 领土


def test_registry_register_and_get():
    reg = NationRegistry()
    reg.register(build_example_nation())
    assert reg.has("emberfall")
    assert reg.get("emberfall").name == "Emberfall 王国"


def test_registry_nation_at():
    reg = build_example_registry()
    assert reg.nation_at(0, 0).nation_id == "emberfall"
    assert reg.nation_at(5, 0).nation_id == "frosthold"
    assert reg.nation_at(100, 100) is None


def test_example_registry_has_two():
    reg = build_example_registry()
    assert len(reg.ids()) == 2


def test_snapshot_round_trip():
    reg = build_example_registry()
    reg2 = NationRegistry.from_snapshot(reg.snapshot())
    assert reg2.has("emberfall")
    assert reg2.get("emberfall").territory.area() == 25
    assert reg2.nation_at(5, 0).nation_id == "frosthold"


def test_economy_integrates_nations():
    from economy import Economy
    eco = Economy()
    eco.nation_registry.register(build_example_nation())
    snap = eco.snapshot()
    assert "nations" in snap
    eco2 = Economy()
    eco2.restore(snap)
    assert eco2.nation_registry.has("emberfall")
