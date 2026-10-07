import json
import re
import os
import sys

# 检查是否有命令行参数
if len(sys.argv) > 1:
    json_file_path = sys.argv[1]
    print(f'Using JSON file: {json_file_path}')
else:
    # 定义文件路径，自行修改词条文件名
    json_file_path = 'zh.json'

missing_files = []

# 读取JSON文件内容
with open(json_file_path, 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)

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
            # 直接字符串替换，不使用正则
            search_str = f'"{original}"'
            replace_str = f'"{new_value}"'
            if search_str in content:
                content = content.replace(search_str, replace_str)

    # 将修改后的内容写回文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

print('Successfully replaced strings in the original files')

if missing_files:
    print('The following files were not found:')
    for missing_file in missing_files:
        print(missing_file)
