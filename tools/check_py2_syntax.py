# -*- coding: utf-8 -*-
"""检查 Mod 脚本是否满足 Python 2.7 语法兼容。

网易 20190712 SDK 的 Mod 运行环境是 Python 2。我们的 core/adapters/runtime
代码必须能被 Python 2.7 解析。本工具做两件事：

1. 用 parso 的 Python 2.7 grammar 解析，报告结构性语法错误（error node）。
2. 用正则扫描 Python 3 独有的语法模式（f-string、async/await、类型注解、
   nonlocal、yield from、dataclass、match、矩阵乘法 @），给出行号。

只检查进入 Minecraft 的脚本目录：core/ adapters/ server/ client/ common/ 与
modMain.py。tools/ 与 tests/ 是 Mac 本机工具，不进 Minecraft，不检查。

用法：
    python3 tools/check_py2_syntax.py <scripts根目录>
    .venv/bin/python tools/check_py2_syntax.py <scripts根目录>   # 若 parso 装在 venv
"""
import os
import re
import sys

# Python 3 独有语法模式（按行扫描，先剥离 # 注释）。
# 注意：装饰器 @decorator 是 Python 2.4+ 合法语法，不算矩阵乘法；不检测 @。
PY3_ONLY_PATTERNS = [
    ('f-string', re.compile(
        r'(?<![A-Za-z0-9_])(?:[fF][rR]?|[rR][fF])'
        r'(?:\'\'\'|\"\"\"|\'|\")')),
    ('async def / await', re.compile(r'\basync\s+def\b|\bawait\b')),
    ('函数返回注解 ->', re.compile(r'\)\s*->')),
    ('nonlocal', re.compile(r'\bnonlocal\b')),
    ('yield from', re.compile(r'\byield\s+from\b')),
    ('dataclass', re.compile(r'\bdataclass\b')),
    ('match 语句', re.compile(r'^\s*match\s+.*:\s*$')),
    ('仅位置参数 /', re.compile(r'def\s+\w+\([^)]*,\s*/\s*[,)]')),
]


def _strip_comment(line):
    """去掉 # 注释（本项目代码字符串内不含 #，故简单切分足够）。"""
    return line.split('#')[0]

# 结构上 Python 2.7 无法解析的错误，parso 会生成 error node。这里列常见的
# error 节点类型名，用于定位。
ERROR_NODE_TYPES = ('error_node', 'error_leaf')


def load_grammar():
    import parso
    return parso.load_grammar(version='2.7')


def iter_py_files(root):
    checked_dirs = ('core', 'adapters', 'server', 'client', 'common')
    for name in os.listdir(root):
        if name in checked_dirs:
            d = os.path.join(root, name)
            if os.path.isdir(d):
                for f in sorted(os.listdir(d)):
                    if f.endswith('.py'):
                        yield os.path.join(d, f)
        elif name == 'modMain.py':
            yield os.path.join(root, name)


def check_parso(grammar, code):
    """返回结构性语法错误列表。"""
    errors = []
    try:
        module = grammar.parse(code)
    except Exception as e:  # 某些情况 parso 直接抛
        return ['parso parse exception: %s' % e]
    for node in module.children:
        _collect_error_nodes(node, errors)
    return errors


def _collect_error_nodes(node, out):
    if getattr(node, 'type', None) in ERROR_NODE_TYPES:
        out.append('error node: %r' % (node.get_code(),))
    for child in getattr(node, 'children', []) or []:
        _collect_error_nodes(child, out)


def check_py3_patterns(code):
    """逐行扫描 Python 3 独有语法，返回 (行号, 描述, 行内容) 列表。"""
    hits = []
    for lineno, line in enumerate(code.splitlines(), 1):
        stripped = _strip_comment(line)
        for desc, pat in PY3_ONLY_PATTERNS:
            if pat.search(stripped):
                hits.append((lineno, desc, line.strip()))
                break  # 每行只报第一条
    return hits


def main(argv):
    if len(argv) < 1:
        print(__doc__)
        return 2
    root = argv[0]
    if not os.path.isdir(root):
        print('not a directory: %s' % root)
        return 2

    grammar = load_grammar()
    total_errors = 0
    files = list(iter_py_files(root))
    if not files:
        print('no mod scripts found under %s' % root)
        return 0

    for path in files:
        rel = os.path.relpath(path, root)
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()

        problems = []

        parso_errors = check_parso(grammar, code)
        for e in parso_errors:
            problems.append('parso: %s' % e)

        for lineno, desc, line in check_py3_patterns(code):
            problems.append('py3-only(%s) line %d: %s' % (desc, lineno, line))

        if problems:
            total_errors += len(problems)
            print('FAIL %s' % rel)
            for p in problems:
                print('    - %s' % p)
        else:
            print('ok   %s' % rel)

    print('-' * 50)
    if total_errors:
        print('RESULT: %d problem(s) across %d file(s)' % (total_errors, len(files)))
        return 1
    print('RESULT: all %d file(s) Python 2.7 grammar compatible' % len(files))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
