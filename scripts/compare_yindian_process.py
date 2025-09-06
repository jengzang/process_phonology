import os
import pathlib
from common.config import PROCESSED_DATA_DIR, YINDIAN_DATA_DIR


def get_file_info(directory):
    files_info = {}
    for fname in os.listdir(directory):
        if fname.endswith(".tsv"):
            fpath = os.path.join(directory, fname)
            # 统计行数
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                line_count = sum(1 for _ in f)
            # 获取修改时间
            mtime = os.path.getmtime(fpath)
            files_info[fname] = (line_count, mtime)
    return files_info

processed = get_file_info(PROCESSED_DATA_DIR)
yindian = get_file_info(YINDIAN_DATA_DIR)

# 取交集
common_files = set(processed.keys()) & set(yindian.keys())

for fname in sorted(common_files):
    p_lines, p_time = processed[fname]
    y_lines, y_time = yindian[fname]
    print(f"文件: {fname}")
    print(f"  PROCESSED: {p_lines} 行, 时间 {pathlib.Path(PROCESSED_DATA_DIR, fname).stat().st_mtime}")
    print(f"  YINDIAN  : {y_lines} 行, 时间 {pathlib.Path(YINDIAN_DATA_DIR, fname).stat().st_mtime}")
    print(f"  行数差异: {p_lines - y_lines}")
    print("-" * 50)
