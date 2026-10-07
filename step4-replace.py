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

# 提取字符串中所有花括号占位符的内容（不含花括本体）。
# 例如 "{name}" -> ["name"], "{}" -> [""], "{:?}" -> [":?"], "{a}{b}" -> ["a", "b"]
# 用 Counter 做多重集比较：位置无关，但每个占位符的种类与数量必须一致。
_PLACEHOLDER_RE = re.compile(r'\{([^{}]*)\}')

def extract_placeholders(s: str):
    return _PLACEHOLDER_RE.findall(s)

def placeholders_match(original: str, new_value: str) -> bool:
    """译文的占位符多重集必须与原文完全一致，才能保证替换后仍是合法 Rust 字符串。
    返回 True 表示可以替换，False 表示应跳过。"""
    return Counter(extract_placeholders(original)) == Counter(extract_placeholders(new_value))

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
                    print(f'[SKIP] 占位符不一致，拒绝替换: {file_path}: {repr(original)} -> {repr(new_value)}')
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

print(f'Successfully replaced strings in the original files (跳过 {skipped_count} 条占位符不一致的翻译)')

if missing_files:
    print('The following files were not found:')
    for missing_file in missing_files:
        print(missing_file)