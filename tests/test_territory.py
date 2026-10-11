# -*- coding: utf-8 -*-
from territory import Territory


def test_add_and_contains():
    t = Territory()
    t.add_chunk(0, 0)
    t.add_chunk(1, 2)
    assert t.contains(0, 0)
    assert t.contains(1, 2)
    assert not t.contains(9, 9)


def test_remove():
    t = Territory()
    t.add_chunk(0, 0)
    t.remove_chunk(0, 0)
    assert not t.contains(0, 0)


def test_area():
    t = Territory()
    for cx in range(-2, 3):
        for cz in range(-2, 3):
            t.add_chunk(cx, cz)
    assert t.area() == 25


def test_bbox():
    t = Territory()
    t.add_chunk(0, 0)
    t.add_chunk(3, 5)
    t.add_chunk(-2, 1)
    assert t.bbox() == (-2, 0, 3, 5)


def test_render():
    t = Territory()
    for cx in range(3):
        for cz in range(3):
            t.add_chunk(cx, cz)
    rendered = t.render(capital=(1, 1))
    assert rendered == "###\n#@#\n###"


def test_render_empty():
    t = Territory()
    assert t.render() == ""


def test_chunks_sorted():
    t = Territory()
    t.add_chunk(1, 0)
    t.add_chunk(0, 0)
    assert t.chunks() == [(0, 0), (1, 0)]


def test_snapshot_round_trip():
    t = Territory()
    t.add_chunk(0, 0)
    t.add_chunk(1, 2)
    t2 = Territory.from_snapshot(t.snapshot())
    assert t2.area() == 2
    assert t2.contains(1, 2)
