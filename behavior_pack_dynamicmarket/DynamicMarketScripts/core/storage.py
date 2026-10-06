# -*- coding: utf-8 -*-
"""存储接口与内存实现。

Storage 抽象 load/save。MemoryStorage 用于纯核心测试；Runtime 层将实现
Netease2019ExtraDataStorage（网易 extraData 组件）。因 extraData 容量上限
未知（见 docs/RUNTIME_PENDING.md），接口保持简单，未来可无痛增加 chunking。
"""


class Storage(object):
    def load(self):
        """返回已存储的 blob（dict）或 None。"""
        raise NotImplementedError

    def save(self, blob):
        raise NotImplementedError


class MemoryStorage(Storage):
    def __init__(self):
        self._data = None

    def save(self, blob):
        self._data = blob

    def load(self):
        return self._data
