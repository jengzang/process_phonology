import os
import re
import shutil
from pathlib import Path

# === 配置 ===
md_filename = "readme.md"  # 要处理的 Markdown 文件名
target_img_dir = "images"  # 图片保存目录
image_prefix = "image"     # 新文件名前缀，如 image01.png

# === 准备工作 ===
os.makedirs(target_img_dir, exist_ok=True)
with open(md_filename, "r", encoding="utf-8") as f:
    content = f.read()

# 匹配 Markdown 图片语法 ![](路径)
img_pattern = re.compile(r'!\[.*?\]\((.*?)\)')
matches = img_pattern.findall(content)

new_content = content
copied = 0

for idx, old_path in enumerate(matches):
    if old_path.startswith("http") or old_path.startswith("images/"):
        continue  # 跳过远程图片或已经处理过的路径

    # 获取原始文件名扩展名
    old_path_clean = old_path.strip().strip('"').strip("'")
    ext = os.path.splitext(old_path_clean)[1] or ".png"
    new_name = f"{image_prefix}{idx+1:02d}{ext}"
    new_path = os.path.join(target_img_dir, new_name)

    # 复制文件
    try:
        shutil.copy(old_path_clean, new_path)
        print(f"✅ 已复制：{old_path_clean} → {new_path}")
        copied += 1
    except Exception as e:
        print(f"⚠️ 跳过 {old_path_clean}：{e}")
        continue

    # 替换 Markdown 中的路径
    new_content = new_content.replace(old_path, f"{target_img_dir}/{new_name}")

# 保存修改后的 Markdown 文件
backup_path = md_filename.replace(".md", "_bak.md")
shutil.copy(md_filename, backup_path)
with open(md_filename, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"\n🎉 完成：共复制并替换 {copied} 张图片，原文件备份为 {backup_path}")
