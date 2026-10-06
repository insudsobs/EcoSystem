# -*- coding: utf-8 -*-
"""将 20190712 SDK 的 HTML 文档提取为结构化纯文本，便于 grep 核对 API。

用途：Phase 0 调查工具。只读取官方 SDK 文档，不执行任何 .exe。

用法：
    python3 tools/inspect_sdk_docs.py "<sdk目录>/3 Mod SDK/3-1 Mod SDK文档.html"
    python3 tools/inspect_sdk_docs.py <html> --grep <keyword>

注意：本脚本只在 Mac 上运行，不进入 Minecraft，可用 Python 3 语法。
"""
import re
import sys
import html as _html


def strip_html(raw):
    """去除 HTML 标签并保留段落换行结构。"""
    text = raw
    # 去掉脚本与样式块
    text = re.sub(r'<script.*?</script>', '', text, flags=re.S)
    text = re.sub(r'<style.*?</style>', '', text, flags=re.S)
    # 结构性标签转成换行
    for tag in ('br', '/p', '/div', '/tr', '/li', '/h1', '/h2', '/h3',
                '/h4', '/h5', '/td', '/th', '/table'):
        text = re.sub('<' + tag + r'[^>]*>', '\n', text, flags=re.I)
    text = re.sub(r'<[^>]+>', '', text)
    text = _html.unescape(text)
    text = re.sub(r'[ \t]+', ' ', text)
    lines = [l.strip() for l in text.splitlines()]
    return [l for l in lines if l]


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    path = argv[0]
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        raw = f.read()
    lines = strip_html(raw)

    if '--grep' in argv:
        idx = argv.index('--grep')
        if idx + 1 >= len(argv):
            print('missing keyword after --grep')
            return 1
        kw = argv[idx + 1]
        for i, l in enumerate(lines, 1):
            if kw in l:
                print('%d\t%s' % (i, l))
    else:
        for i, l in enumerate(lines, 1):
            print('%d\t%s' % (i, l))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
