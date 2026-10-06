# -*- coding: utf-8 -*-
"""状态序列化与校验（MarketState codec）。

MarketState 是纯 JSON-compatible dict（dict/list/int/str/bool/null），
禁止 pickle、禁止直接序列化 class instance。encode 附加 schemaVersion /
configVersion / savedAt / checksum；decode 校验 checksum 并做版本迁移。

canonical serialization：sort_keys + 固定分隔符，保证 Python 2.7 与
Python 3 结果语义一致。checksum 用 sha256。
"""
import json
import hashlib
from errors import StorageCorrupted, SchemaVersionError

SCHEMA_VERSION = 1


def canonical_dump(data):
    """canonical 序列化（跨解释器稳定）。"""
    return json.dumps(data, sort_keys=True, separators=(',', ':'))


def checksum_of(data):
    raw = canonical_dump(data)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def encode(market_state, saved_at=0):
    """market_state 为纯 dict，返回可存入 extraData 的 blob。"""
    return {
        "schemaVersion": SCHEMA_VERSION,
        "configVersion": market_state.get("configVersion", 0),
        "savedAt": saved_at,
        "data": market_state,
        "checksum": checksum_of(market_state),
    }


def decode(blob):
    """校验并返回 market_state。checksum 不匹配抛 StorageCorrupted。"""
    version = blob.get("schemaVersion", 0)
    data = blob.get("data")
    stored_checksum = blob.get("checksum")
    if data is None or stored_checksum is None:
        raise StorageCorrupted("missing data or checksum in blob")

    if checksum_of(data) != stored_checksum:
        raise StorageCorrupted("checksum mismatch: stored %r != computed %r"
                               % (stored_checksum, checksum_of(data)))

    if version > SCHEMA_VERSION:
        raise SchemaVersionError(
            "schema version %r newer than supported %r" % (version, SCHEMA_VERSION))
    if version < SCHEMA_VERSION:
        data = migrate(version, data)
    return data


def migrate(from_version, data):
    """版本迁移。Phase 1.5 仅 version 1，无历史迁移路径。"""
    raise SchemaVersionError(
        "no migration path from schema version %r" % from_version)
