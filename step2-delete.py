import sys
import json
import yaml
import re
import os
from collections import Counter

# 定义文件路径
json_file_path = 'string.json'
yaml_file_path = 'del.yaml'


def should_delete(key, keys_to_delete, patterns=()):
    """判定键名是否应删除；返回命中规则字符串，不删除返回 None。"""
    # 检查精确匹配规则（global 或按文件列表）
    if key in keys_to_delete:
        return '精确匹配'

    # 检查正则模式规则（del.yaml 的 global_patterns）
    for pattern in patterns:
        if pattern.search(key):
            return f'正则: {pattern.pattern}'

    # 检查是否为网址
    if re.match(r'https?://', key):
        return '内置:网址'

    # 检查是否为文件路径
    if re.match(r'^(?:[a-zA-Z]:[\\/]|[\\/]|\.{1,2}[\\/]).+\.[a-zA-Z0-9]{1,5}$', key):
        return '内置:文件路径'

    # 检查是否为纯数字
    if key.isdigit():
        return '内置:纯数字'

    # 检查是否为纯标点符号
    if re.match(r'^[^\w\s]+$', key):
        return '内置:纯标点'

    return None


def delete_keys_from_dict(data, keys_to_delete, level=1, patterns=(), section=None, deleted=None):
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if level == 2:
                reason = should_delete(key, keys_to_delete, patterns)
                if reason is not None:
                    if deleted is not None:
                        deleted.append({
                            'file': section if section is not None else key,
                            'key': key,
                            'rule': reason,
                        })
                    continue
            result[key] = delete_keys_from_dict(
                value, keys_to_delete, level + 1, patterns,
                section=key if section is None else section, deleted=deleted)
        return result
    if isinstance(data, list):
        return [delete_keys_from_dict(item, keys_to_delete, level, patterns,
                                      section=section, deleted=deleted) for item in data]
    return data


def main(input_file: str, deletes: str):

    # 读取JSON文件内容
    with open(input_file, 'r', encoding='utf-8') as json_file:
        json_data = json.load(json_file)

    # 读取YAML文件内容
    with open(deletes, 'r', encoding='utf-8') as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)

    # 获取全局删除规则
    global_keys_to_delete = yaml_data.get('global', [])

    # 获取全局正则模式规则（键名匹配任一正则即删除）
    global_patterns = [re.compile(p) for p in yaml_data.get('global_patterns', [])]

    # 获取段级正则规则（顶层文件段名匹配任一正则即整段删除）
    section_patterns = [re.compile(p) for p in yaml_data.get('section_patterns', [])]

    # 删除明细：每项 {"file": 来源文件段, "key": 键名, "rule": 命中规则}
    deleted = []

    # 整段删除：段名命中 section_patterns 的段，其全部键一并记录
    for section in list(json_data):
        pat_text = next((p.pattern for p in section_patterns if p.match(section)), None)
        if pat_text is None:
            continue
        entries = json_data[section]
        if isinstance(entries, dict):
            for key in entries:
                deleted.append({'file': section, 'key': key,
                                'rule': f'段级整段删除: {pat_text}'})
        else:
            deleted.append({'file': section, 'key': '<整段>',
                            'rule': f'段级整段删除: {pat_text}'})
        del json_data[section]

    # 遍历JSON数据并删除全局规则中的键（记录明细）
    json_data = delete_keys_from_dict(json_data, global_keys_to_delete,
                                      patterns=global_patterns, deleted=deleted)

    # 遍历YAML数据并删除JSON数据中的对应项
    for file_path, keys_to_delete in yaml_data.items():
        if file_path in ('global', 'global_patterns', 'section_patterns'):
            continue
        if file_path in json_data:
            json_data[file_path] = delete_keys_from_dict(
                json_data[file_path], keys_to_delete, level=2, patterns=global_patterns,
                section=file_path, deleted=deleted)

    # 将修改后的内容写回JSON文件
    with open(input_file, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=2)

    # 输出删除明细到日志文件（JSONL，每行一个 {"file","key","rule"}；键含换行也能安全记录）
    log_dir = os.path.dirname(input_file) or '.'
    log_name = os.path.splitext(os.path.basename(input_file))[0] + '.deleted.log'
    log_path = os.path.join(log_dir, log_name)
    with open(log_path, 'w', encoding='utf-8') as log_file:
        for entry in deleted:
            log_file.write(json.dumps(entry, ensure_ascii=False) + '\n')

    # 控制台输出统计摘要
    print(f'Successfully deleted {len(deleted)} keys from {input_file}, details -> {log_path}')
    by_rule = Counter(e['rule'] for e in deleted)
    print('按命中规则统计 (top 15):')
    for rule, n in by_rule.most_common(15):
        print(f'  {n:>6}  {rule}')
    by_file = Counter(e['file'] for e in deleted)
    print('按来源文件段统计 (top 10):')
    for sec, n in by_file.most_common(10):
        print(f'  {n:>6}  {sec}')


if __name__ == '__main__':
    args = sys.argv
    # 默认参数
    input_file = json_file_path
    deletes = yaml_file_path
    if len(args) >= 2:
        input_file = args[1]
    if len(args) >= 3:
        deletes = args[2]

    main(input_file, deletes)
