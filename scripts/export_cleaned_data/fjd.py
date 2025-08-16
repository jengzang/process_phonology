import csv
import re
import os
from io import StringIO

import pandas as pd
from pathlib import Path
from collections import defaultdict
import ast


# 替代 ast.literal_eval 的解析方法
def parse_sql_tuple(tup_str):
    # 将 SQL 格式的 (value1, 'value2', 'value3') 转为 CSV 行
    fake_csv = StringIO(tup_str.strip()[1:-1])  # 去掉外层括号
    reader = csv.reader(fake_csv, delimiter=',', quotechar="'", skipinitialspace=True)
    return next(reader)


# === 配置 ===
SQL_FILE = "rawdata/jyutdict.sql"
OUTPUT_DIR = Path("fjd处理后")
OUTPUT_DIR.mkdir(exist_ok=True)

# === Step 1: 读取 SQL 文件 ===
with open(SQL_FILE, encoding="utf-8") as f:
    sql_text = f.read()

# === Step 2: 提取所有 INSERT INTO 语句 ===
table_data = defaultdict(list)
parse_stats = defaultdict(lambda: {"tried": 0, "success": 0})
insert_pattern = re.compile(
    r"INSERT INTO [`\"]?(\w+)[`\"]?\s*\(([^)]+)\)\s*VALUES\s*(.*?);",
    re.DOTALL
)

for match in insert_pattern.finditer(sql_text):
    table_name = match.group(1)
    columns = [c.strip(" `\"") for c in match.group(2).split(",")]
    values_block = match.group(3)

    # 修正后的正则，提取完整元组（即使字段里有括号）
    tuples = re.findall(r"\((?:[^()']|'[^']*')+\)", values_block)
    for idx, tup in enumerate(tuples):
        parse_stats[table_name]["tried"] += 1  # 每次尝试都加一
        try:
            # 尝试用 ast 解析出元组
            # row = ast.literal_eval(tup)
            row = parse_sql_tuple(tup)
            if len(row) != len(columns):
                print(f"⚠️ 第 {idx} 行列数不一致：{len(row)} vs {len(columns)}")
                print(f"   ➤ 解析结果：{row}")
                print(f"   ➤ 原始元组：{tup}")
                continue
            # table_data[table_name].append(dict(zip(columns, row)))


            # 清理字符串中形如 '(書)' 的字段 → '書'
            cleaned_row = []
            for item in row:
                if isinstance(item, str) and re.fullmatch(r"\([^\(\)]+\)", item):
                    cleaned_row.append(item[1:-1])  # 去掉首尾括号
                else:
                    cleaned_row.append(item)

            table_data[table_name].append(dict(zip(columns, cleaned_row)))
            parse_stats[table_name]["success"] += 1  # 只有这时才统计为成功

        except Exception as e:
            print("❌ 无法解析：")
            print(f"  ➤ 行号       ：{idx + 1}")
            print(f"  ➤ 原始内容   ：{tup}")
            print(f"  ➤ 错误类型   ：{type(e).__name__}")
            print(f"  ➤ 错误详情   ：{e}")

# === Step 3: 构建 IAreaList 映射表，用于命名 ===
area_map = {}
if "IAreaList" in table_data:
    for row in table_data["IAreaList"]:
        sheetname = row.get("sheetname", "")
        second = row.get("second", "") or ""
        third = row.get("third", "") or ""
        filename = f"{second}{third}".strip() or sheetname
        area_map[sheetname] = filename

# === Step 4: 导出每个表为 Excel ===
for table, rows in table_data.items():
    if table == "IAreaList":
        continue
    if not rows:
        print(f"⚠️ 空表跳过：{table}")
        continue

    df = pd.DataFrame(rows)

    # 重命名列
    df.rename(columns={
        "chara": "漢字",
        "note": "notes"
    }, inplace=True)

    # 文件名
    filename = area_map.get(table, table)
    out_path = OUTPUT_DIR / f"{filename}.xlsx"

    exported = len(df)
    tried = parse_stats[table]["tried"]
    success = parse_stats[table]["success"]
    ignored = tried - success

    df.to_excel(out_path, index=False)
    print(f"✅ 导出：{out_path.name}，共 {exported} 行，有 {ignored} 行被忽略")

print("\n=== 📦 开始 IPA 拆分后处理 ===")

for excel_file in OUTPUT_DIR.glob("*.xlsx"):
    df = pd.read_excel(excel_file)
    if "ipa" not in df.columns:
        print(f"⚠️ 文件 {excel_file.name} 缺少 ipa 列，跳过")
        continue

    new_rows = []
    split_count = 0
    total_split_lines = 0

    for idx, row in df.iterrows():
        ipa_value = str(row["ipa"])
        if "=" in ipa_value:
            split_ipas = ipa_value.split("=")
            total_split_lines += len(split_ipas)
            split_count += 1
            print(f"  ➤ 第 {idx+1} 行 ipa 拆分为 {len(split_ipas)} 项：{split_ipas}")
            for ipa in split_ipas:
                new_row = row.copy()
                new_row["ipa"] = ipa.strip()
                new_rows.append(new_row)
        else:
            new_rows.append(row)

    new_df = pd.DataFrame(new_rows)
    new_df.to_excel(excel_file, index=False)
    print(f"✅ 文件 {excel_file.name}：拆分 {split_count} 行，新增 {total_split_lines - split_count} 行，"
          f"最终总数 {len(new_df)} 行")