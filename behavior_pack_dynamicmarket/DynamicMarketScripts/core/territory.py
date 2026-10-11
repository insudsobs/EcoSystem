# -*- coding: utf-8 -*-
"""国家领土（Territory）：chunk 坐标集合 + ASCII 版图显示。

纯核心，不依赖网易。领土用 (cx, cz) chunk 坐标（整数）表示；内存用 set
存 "cx,cz" 字符串（可哈希、可序列化，避免 tuple 序列化问题）。版图显示用
ASCII 网格，方便 Mac 上直接测试与调试。
"""


def _key(cx, cz):
    return "%d,%d" % (cx, cz)


def _parse(key):
    cx, cz = key.split(",")
    return int(cx), int(cz)


class Territory(object):
    """国家领土：一组 chunk 坐标 (cx, cz)。"""

    def __init__(self):
        self._chunks = set()

    def add_chunk(self, cx, cz):
        self._chunks.add(_key(cx, cz))

    def remove_chunk(self, cx, cz):
        self._chunks.discard(_key(cx, cz))

    def contains(self, cx, cz):
        return _key(cx, cz) in self._chunks

    def area(self):
        """领土面积（chunk 数）。"""
        return len(self._chunks)

    def chunks(self):
        """排序后的 (cx, cz) 列表。"""
        return sorted(_parse(k) for k in self._chunks)

    def bbox(self):
        """边界框 (min_cx, min_cz, max_cx, max_cz)，空领土返回 None。"""
        if not self._chunks:
            return None
        coords = [_parse(k) for k in self._chunks]
        min_cx = min(c for c, _ in coords)
        max_cx = max(c for c, _ in coords)
        min_cz = min(z for _, z in coords)
        max_cz = max(z for _, z in coords)
        return (min_cx, min_cz, max_cx, max_cz)

    def render(self, capital=None, mark="#", empty="."):
        """ASCII 版图显示。capital 为 (cx, cz) 或 None。

        网格：列 = cx（左到右），行 = cz（上到下，即 cz 从大到小）。
        领土格子用 mark，首都用 @，空白用 empty。
        """
        if not self._chunks:
            return ""
        min_cx, min_cz, max_cx, max_cz = self.bbox()
        rows = []
        for cz in range(max_cz, min_cz - 1, -1):
            row = []
            for cx in range(min_cx, max_cx + 1):
                if capital is not None and (cx, cz) == capital:
                    row.append("@")
                elif self.contains(cx, cz):
                    row.append(mark)
                else:
                    row.append(empty)
            rows.append("".join(row))
        return "\n".join(rows)

    def snapshot(self):
        return sorted(self._chunks)

    @classmethod
    def from_snapshot(cls, chunks):
        obj = cls()
        for k in chunks:
            obj._chunks.add(k)
        return obj
