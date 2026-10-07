import json
import re
import os
import sys
from collections import Counter

# 检查是否有命令行参数
if len(sys.argv) > 1:
    json_file_path = sys.argv[1]
    print(f'Using JSON file: {json_file_path}')
else:
    # 定义文件路径，自行修改词条文件名
    json_file_path = 'zh.json'

missing_files = []

# Rust 格式占位符正则：匹配 {name}、{}、{:?}、{name:?} 等格式字符串
# 不匹配纯数字的 {4}（正则量词）或 \u{hex}（转义序列）
_RUST_FORMAT_RE = re.compile(r'\{([^}]*[^}\s][^}]*)\}')
# Rust 转义序列正则
_RUST_ESCAPE_RE = re.compile(r'\\u\{[0-9a-fA-F]+\}|\\x[0-9a-fA-F]{2}')

def extract_placeholders(s: str):
    """提取 Rust format! 占位符，排除转义序列和纯数字量词。

    Rust 格式占位符特征：
    - 名字：字母开头，如 {name}, {_var}
    - 空：{}, 表示位置参数
    - 格式说明：:{:?}, :>10, :05 等

    排除情况：
    - \\u{hex} 转义序列
    - {4} 这样的纯数字正则量词
    - {1,3} 这样的范围量词
    """
    # 先把 \u{hex} 转义序列替换掉，避免误判
    parts = []
    last_end = 0
    for m in _RUST_ESCAPE_RE.finditer(s):
        parts.append(s[last_end:m.start()])
        parts.append('\x00')  # 保护标记
        last_end = m.end()
    parts.append(s[last_end:])
    protected = ''.join(parts)

    # 提取候选占位符
    result = _RUST_FORMAT_RE.findall(protected)
    # 过滤：纯数字或数字范围（正则量词）不是占位符
    return [p for p in result if not re.match(r'^\d+(,\d+)?$', p)]

def placeholders_match(original: str, new_value: str) -> bool:
    """译文的占位符多重集必须与原文完全一致，才能保证替换后仍是合法 Rust 字符串。
    返回 True 表示可以替换，False 表示应跳过。"""
    return Counter(extract_placeholders(original)) == Counter(extract_placeholders(new_value))

def safe_print(*args, **kwargs):
    """安全的打印函数，处理 Windows 编码问题"""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Windows 下遇到编码错误时，强制使用 ASCII 替换
        for arg in args:
            try:
                print(arg, end=kwargs.get('end', ''), flush=True)
            except UnicodeEncodeError:
                print(str(arg).encode('utf-8', errors='replace').decode('utf-8'), end='', flush=True)
        if kwargs.get('end') and kwargs['end'] != '\n':
            print(end=kwargs['end'])
        print(flush=True)

# 读取JSON文件内容
with open(json_file_path, 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)

skipped_count = 0

# 遍历JSON数据
for file_path, replacements in json_data.items():
    if not os.path.exists(file_path):
        missing_files.append(file_path)
        continue

    # 读取原始文件内容
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 替换非空值（使用简单字符串替换，避免正则转义问题）
    for original, new_value in replacements.items():
        if new_value and original:  # 如果值不为空且键不为空
            # 【占位符保护】原文含花括号占位符（如 Rust format! 的 {name}/{}/{:?}）时，
            # 译文的占位符种类与数量必须与原文完全一致，否则替换后会破坏编译。
            # 典型错误：把 "{prefix}\n\n{suffix}" 译成 "\n\n"（丢光占位符）。
            if extract_placeholders(original):
                if not placeholders_match(original, new_value):
                    safe_print(f'[SKIP] 占位符不一致，拒绝替换: {file_path}: {repr(original)} -> {repr(new_value)}')
                    skipped_count += 1
                    continue

            # 直接字符串替换，不使用正则
            search_str = f'"{original}"'
            replace_str = f'"{new_value}"'
            if search_str in content:
                content = content.replace(search_str, replace_str)

    # 将修改后的内容写回文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

safe_print(f'Successfully replaced strings in the original files (跳过 {skipped_count} 条占位符不一致的翻译)')

if missing_files:
    safe_print('The following files were not found:')
    for missing_file in missing_files:
        safe_print(missing_file)