#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频链接自动替换脚本
将文章中的本地视频路径替换为 Cloudflare R2 的 CDN 链接
"""

import os
import re
import sys
from pathlib import Path

def load_url_mapping(mapping_file="video_url_mapping.txt"):
    """
    加载视频 URL 映射文件
    格式: 本地路径|CDN链接
    """
    mapping = {}
    
    if not os.path.exists(mapping_file):
        print(f"⚠️  未找到映射文件: {mapping_file}")
        return mapping
    
    with open(mapping_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if '|' in line:
                local_path, cdn_url = line.split('|', 1)
                mapping[local_path] = cdn_url
    
    print(f"✅ 加载了 {len(mapping)} 个视频映射")
    return mapping

def find_markdown_files(content_dir="content"):
    """
    递归查找所有 Markdown 文件
    """
    markdown_files = []
    content_path = Path(content_dir)
    
    if not content_path.exists():
        print(f"❌ 内容目录不存在: {content_dir}")
        return markdown_files
    
    for md_file in content_path.rglob("*.md"):
        markdown_files.append(str(md_file))
    
    print(f"📄 找到 {len(markdown_files)} 个 Markdown 文件")
    return markdown_files

def replace_video_links_in_file(file_path, mapping):
    """
    在单个文件中替换视频链接
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 读取文件失败 {file_path}: {e}")
        return False
    
    original_content = content
    changes_made = False
    
    # 匹配视频链接的正则表达式
    video_patterns = [
        # 标准 Markdown 语法
        r'\[([^\]]*(?:视频|video|播放)[^\]]*)\]\(([^)]+\.(?:mp4|webm|mov|avi|mkv))\)',
        # 直接的文件路径
        r'(?:src|href)="([^"]+\.(?:mp4|webm|mov|avi|mkv))"',
        # 普通的文件路径引用
        r'([^\s<>()\[\]]+\.(?:mp4|webm|mov|avi|mkv))',
    ]
    
    for local_path, cdn_url in mapping.items():
        # 尝试多种匹配模式
        for pattern in video_patterns:
            # 创建替换函数
            def replacer(match):
                nonlocal changes_made
                full_match = match.group(0)
                
                # 检查是否包含我们要替换的本地路径
                if local_path in full_match:
                    # 保持原有的格式，只替换 URL 部分
                    if match.groups():
                        # 如果有分组（比如 Markdown 链接）
                        groups = list(match.groups())
                        # 替换包含本地路径的组
                        for i, group in enumerate(groups):
                            if local_path in group:
                                groups[i] = cdn_url
                        
                        # 重新构造匹配
                        result = full_match
                        for i, group in enumerate(groups):
                            if i == 0:
                                result = result.replace(group, groups[i], 1)
                        return result
                    else:
                        # 直接替换
                        return full_match.replace(local_path, cdn_url)
                else:
                    return full_match
            
            # 执行替换
            content = re.sub(pattern, replacer, content, flags=re.IGNORECASE)
        
        # 检查是否有变化
        if content != original_content:
            changes_made = True
    
    # 如果有变化，写回文件
    if changes_made:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 更新: {file_path}")
            return True
        except Exception as e:
            print(f"❌ 写入文件失败 {file_path}: {e}")
            return False
    else:
        print(f"⏭️  无需更新: {file_path}")
        return True

def create_video_shortcode(local_path, cdn_url):
    """
    创建 Hugo 视频短代码
    """
    filename = os.path.basename(local_path)
    file_ext = os.path.splitext(filename)[1][1:]  # 去掉点号
    
    shortcode = f"""{{{{< video src="{cdn_url}" type="video/{file_ext}" title="{filename}" >}}}}
"""
    
    return shortcode

def generate_video_embeds(mapping, output_file="video_embeds.md"):
    """
    生成视频嵌入代码文档
    """
    embed_content = "# 视频嵌入代码\n\n"
    
    for local_path, cdn_url in mapping:
        filename = os.path.basename(local_path)
        embed_content += f"## {filename}\n\n"
        embed_content += f"**本地路径**: `{local_path}`\n\n"
        embed_content += f"**CDN 链接**: {cdn_url}\n\n"
        embed_content += f"**嵌入代码**:\n\n```html\n"
        embed_content += f'<video controls><source src="{cdn_url}" type="video/{os.path.splitext(filename)[1][1:]}">您的浏览器不支持视频标签。</video>\n'
        embed_content += "```\n\n"
        embed_content += f"**Hugo 短代码**:\n\n"
        embed_content += f"```hugo\n{create_video_shortcode(local_path, cdn_url)}\n```\n\n"
        embed_content += "---\n\n"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(embed_content)
    
    print(f"📝 生成视频嵌入文档: {output_file}")

def main():
    """
    主函数
    """
    print("🎬 视频链接替换工具")
    print("=" * 50)
    
    # 检查映射文件
    mapping = load_url_mapping()
    if not mapping:
        print("❌ 没有找到视频映射，请先运行上传脚本")
        sys.exit(1)
    
    # 查找 Markdown 文件
    markdown_files = find_markdown_files()
    if not markdown_files:
        print("❌ 没有找到 Markdown 文件")
        sys.exit(1)
    
    # 替换链接
    success_count = 0
    for md_file in markdown_files:
        if replace_video_links_in_file(md_file, mapping):
            success_count += 1
    
    print(f"\n🎉 完成! 成功处理 {success_count}/{len(markdown_files)} 个文件")
    
    # 生成视频嵌入文档
    generate_video_embeds(mapping)
    
    print("\n📋 下一步操作:")
    print("1. 检查更新后的 Markdown 文件")
    print("2. 查看生成的 video_embeds.md 获取嵌入代码")
    print("3. 运行 hugo server 预览网站")
    print("4. 提交更改到 Git")

if __name__ == "__main__":
    main()