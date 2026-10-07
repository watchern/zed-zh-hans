import json
import re
import os
import sys
from collections import Counter

# Windows runner 控制台默认 cp1252 编码，打印中文会抛 UnicodeEncodeError。
# 在脚本入口强制将标准输出/错误流重配置为 UTF-8（errors='replace' 兜底）。
for _stream in (sys.stdout, sys.stderr):
    if _stream is not None and hasattr(_stream, 'reconfigure'):
        _stream.reconfigure(encoding='utf-8', errors='replace')

# 检查是否有命令行参数
if len(sys.argv) > 1:
    json_file_path = sys.argv[1]
    print(f'Using JSON file: {json_file_path}')
else:
    # 定义文件路径，自行修改词条文件名
    json_file_path = 'zh.json'

missing_files = []

# ---------------------------------------------------------------------------
# 占位符提取：识别 Rust format! 的 {name}/{}/{:?}，排除转义序列与正则量词
# ---------------------------------------------------------------------------
_PLACEHOLDER_RE = re.compile(r'\{([^{}]*)\}')
_RUST_ESCAPE_RE = re.compile(r'\\u\{[0-9a-fA-F]+\}|\\x[0-9a-fA-F]{2}')

def extract_placeholders(s: str):
    # 先把 \u{hex} 转义序列替换为保护标记，避免其中的花括号被误判为占位符
    parts = []
    last_end = 0
    for m in _RUST_ESCAPE_RE.finditer(s):
        parts.append(s[last_end:m.start()])
        parts.append('\x00')  # 保护标记
        last_end = m.end()
    parts.append(s[last_end:])

    result = _PLACEHOLDER_RE.findall(''.join(parts))
    # 过滤纯数字/数字范围（正则量词，如 {4}、{1,3}）
    return [p for p in result if not re.match(r'^\d+(,\d+)?$', p)]

def placeholders_match(original: str, new_value: str) -> bool:
    """译文的占位符多重集必须与原文完全一致，否则替换后 format! 参数不匹配、编译失败。"""
    return Counter(extract_placeholders(original)) == Counter(extract_placeholders(new_value))

def extract_escapes(s: str):
    """提取 Rust 转义序列（\\u{hex} / \\xHH）多重集。
    转义序列是代码的一部分，译文若将其剥离（如 \\u{0301} 变成非法的 \\u）会直接编译失败。"""
    return Counter(m.group(0) for m in _RUST_ESCAPE_RE.finditer(s))

# ---------------------------------------------------------------------------
# Rust 词法扫描：找出所有字符串字面量的精确位置
# 目的：替换只允许发生在字符串字面量内部，防止片段 key 匹配到代码上下文
# 而破坏源码结构（典型事故：删除了代码里的 } 导致 unclosed delimiter）。
# ---------------------------------------------------------------------------
def scan_string_literals(src: str):
    """扫描 Rust 源码，返回 字面量内容 -> [(起, 止, 前缀, 后缀)] 的映射。
    (起, 止) 为整个字面量 token（含前缀和引号）在源码中的偏移；
    前缀/后缀 形如 '"'/'"'、'b"'/''、'r#"'/'"#'，替换时需原样保留。"""
    literals = {}
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        # 行注释
        if c == '/' and i + 1 < n and src[i + 1] == '/':
            j = src.find('\n', i)
            i = n if j == -1 else j
            continue
        # 块注释（支持嵌套）
        if c == '/' and i + 1 < n and src[i + 1] == '*':
            depth, j = 1, i + 2
            while j < n and depth:
                if src.startswith('/*', j):
                    depth += 1
                    j += 2
                elif src.startswith('*/', j):
                    depth -= 1
                    j += 2
                else:
                    j += 1
            i = j
            continue
        # 原始字符串 r"..." / r#"..."# / br#"..."#
        if c == 'r' or (c == 'b' and i + 1 < n and src[i + 1] == 'r'):
            j = i + (2 if c == 'b' else 1)
            k = j
            while k < n and src[k] == '#':
                k += 1
            hashes = k - j
            if k < n and src[k] == '"':
                start = i
                end = k + 1  # 开引号之后
                while end < n:
                    if src[end] == '"':
                        h2 = end + 1
                        while h2 < n and src[h2] == '#':
                            h2 += 1
                        if h2 - (end + 1) == hashes:
                            break
                        end = h2
                    else:
                        end += 1
                close = min(end + hashes + 1, n)  # 终止引号 + hashes 个 #
                prefix = src[start:k + 1]         # 如 r#" 或 r"
                suffix = src[end:close]           # 如 "# 或 "（含闭合引号）
                content = src[k + 1:end]
                literals.setdefault(content, []).append((start, close, prefix, suffix))
                i = close
                continue
            # 不是原始字符串（如 return、r#ident），主循环逐字符前进
            i += 1
            continue
        # 字节字符串 b"..."
        if c == 'b' and i + 1 < n and src[i + 1] == '"':
            j = i + 2
            while j < n:
                if src[j] == '\\':
                    j += 2
                    continue
                if src[j] == '"':
                    break
                j += 1
            j = min(j, n - 1)
            literals.setdefault(src[i + 2:j], []).append((i, j + 1, 'b"', '"'))
            i = j + 1
            continue
        # 普通字符串 "..."（处理转义）
        if c == '"':
            j = i + 1
            while j < n:
                if src[j] == '\\':
                    j += 2
                    continue
                if src[j] == '"':
                    break
                j += 1
            j = min(j, n - 1)
            literals.setdefault(src[i + 1:j], []).append((i, j + 1, '"', '"'))
            i = j + 1
            continue
        # 字符字面量与生命周期
        if c == "'":
            if i + 1 < n and src[i + 1] == '\\':
                j = i + 1
                while j < n:
                    if src[j] == '\\':
                        j += 2
                        continue
                    if src[j] == "'":
                        break
                    j += 1
                i = min(j + 1, n)
                continue
            if i + 2 < n and src[i + 2] == "'":
                i += 3
                continue
            # 生命周期 'a / 'static
            j = i + 1
            while j < n and (src[j].isalnum() or src[j] == '_'):
                j += 1
            i = j
            continue
        i += 1
    return literals

# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
with open(json_file_path, 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)

skip_placeholder = 0
skip_context = 0
skip_quote = 0
skip_escape = 0

for file_path, replacements in json_data.items():
    if not os.path.exists(file_path):
        missing_files.append(file_path)
        continue

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 快速预检：若所有 key 都不在文件中出现，跳过词法分析
    candidates = []
    for original, new_value in replacements.items():
        if not new_value or not original or new_value == original:
            continue
        if f'"{original}"' in content:
            candidates.append((original, new_value))
    if not candidates:
        continue

    literals = scan_string_literals(content)

    # 收集 (起, 止, 新token) 并从后往前替换，避免偏移失效
    edits = []
    for original, new_value in candidates:
        # 守卫 1：译文不能含未转义的双引号，否则会提前终止字符串字面量
        if re.search(r'(?<!\\)"', new_value):
            print(f'[SKIP] 译文含未转义双引号，拒绝替换: {file_path}: {repr(original)} -> {repr(new_value)}')
            skip_quote += 1
            continue
        # 守卫 2：译文不能以奇数个反斜杠结尾，否则会转义闭合引号
        if re.search(r'(?:^|[^\\])(\\\\)*\\$', new_value):
            print(f'[SKIP] 译文以反斜杠结尾，拒绝替换: {file_path}: {repr(original)}')
            skip_quote += 1
            continue
        # 守卫 3：转义序列必须原样保留（防止 \u{0301} 被剥成非法的 \u 导致编译失败）
        if extract_escapes(original) != extract_escapes(new_value):
            print(f'[SKIP] 转义序列被丢弃，拒绝替换: {file_path}: {repr(original)} -> {repr(new_value)}')
            skip_escape += 1
            continue
        # 守卫 4：占位符多重集必须一致（保护 Rust format! 参数）
        if extract_placeholders(original) and not placeholders_match(original, new_value):
            print(f'[SKIP] 占位符不一致，拒绝替换: {file_path}: {repr(original)} -> {repr(new_value)}')
            skip_placeholder += 1
            continue
        # 守卫 4：原文必须完整命中某个字符串字面量（防止替换到代码上下文）
        spans = literals.get(original)
        if not spans:
            print(f'[SKIP] 原文不在字符串字面量内（疑似代码片段），拒绝替换: {file_path}: {repr(original)}')
            skip_context += 1
            continue
        for start, end, prefix, suffix in spans:
            edits.append((start, end, prefix + new_value + suffix))

    if edits:
        for start, end, token in sorted(edits, key=lambda e: e[0], reverse=True):
            content = content[:start] + token + content[end:]
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

print(f'Successfully replaced strings in the original files '
      f'(跳过 {skip_placeholder} 条占位符不一致, {skip_escape} 条转义序列丢失, '
      f'{skip_context} 条非字符串上下文, {skip_quote} 条引号不安全)')

if missing_files:
    print('The following files were not found:')
    for missing_file in missing_files:
        print(missing_file)