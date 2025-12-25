#!/usr/bin/env python3
import csv
import os
import re
from pathlib import Path

def load_mapping(csv_file):
    mapping = {}
    if os.path.exists(csv_file):
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    mapping[row[0]] = row[1]
    return mapping

def update_links_in_file(file_path, mapping):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    for local_path, cdn_url in mapping.items():
        content = content.replace(local_path, cdn_url)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"已更新: {file_path}")
        return True
    return False

def main():
    content_dir = Path('hugo/content')
    
    print("加载链接映射表...")
    inline_mapping = load_mapping('media/inline-mapping.csv')
    notebooklm_mapping = load_mapping('media/notebooklm-mapping.csv')
    
    all_mapping = {**inline_mapping, **notebooklm_mapping}
    
    if not all_mapping:
        print("未找到映射表，跳过更新")
        return
    
    print(f"找到 {len(all_mapping)} 个映射")
    
    updated_count = 0
    for md_file in content_dir.rglob('*.md'):
        if update_links_in_file(md_file, all_mapping):
            updated_count += 1
    
    print(f"\n更新完成！共更新 {updated_count} 个文件")

if __name__ == '__main__':
    main()
