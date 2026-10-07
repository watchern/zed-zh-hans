import re
import json
import os
import glob

# 注：自动扫描 zed/crates 目录下的 Rust 源文件
# 运行：python3 extract.py
# 输出：string.json

# 定义扫描目录
scan_base = 'zed/crates'
output_file_path = 'string.json'

# 初始化JSON数据
json_data = {}

# 自动发现所有 Rust 源文件（只取 src/ 下的文件）
rust_files = []
for root, dirs, files in os.walk(scan_base):
    # 跳过 examples, tests, test-data, benches 等目录
    dirs[:] = [d for d in dirs if d not in ['examples', 'tests', 'test-data', 'benches']]
    for file in files:
        if file.endswith('.rs'):
            file_path = os.path.join(root, file)
            # 只处理 src/ 目录下的文件
            if '/src/' in file_path.replace('\\', '/') or '\\src\\' in file_path:
                rust_files.append(file_path)

print(f'Found {len(rust_files)} Rust source files in {scan_base}')

# 遍历每个文件路径
for input_file_path in rust_files:
    # 标准化路径，使用正斜杠（与原始 extract.py 保持一致）
    normalized_path = os.path.normpath(input_file_path).replace('\\', '/')

    # 读取文件内容
    try:
        with open(input_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        print(f'Error reading {normalized_path}: {e}')
        continue

    # 先排除掉包含 "json_path:" 的行，然后再提取引号中的内容
    filtered_content = re.sub(r'json_path:\s*".*?"', '', content)

    # 使用正则提取引号中的字符串
    pattern = r'"((?:\\.|[^"\\])*)"'
    matches = re.findall(pattern, filtered_content)

    # 去重并保持顺序
    seen = set()
    unique_matches = []
    for match in matches:
        if match not in seen:
            seen.add(match)
            unique_matches.append(match)

    # 构建JSON数据
    json_data[normalized_path] = {match: "" for match in unique_matches}

# 将JSON数据写入文件
with open(output_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(json_data, json_file, ensure_ascii=False, indent=4)

print(f'Successfully extracted strings to {output_file_path}')
print(f'Total files processed: {len(json_data)}')
print(f'Total strings extracted: {sum(len(v) for v in json_data.values())}')