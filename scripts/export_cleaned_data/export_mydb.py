import sqlite3
import pandas as pd
import os

from common.config import DIALECTS_DB_PATH

# 配置路径
EXCEL_PATH = 'need.xlsx'  # 需要在当前目录下
OUTPUT_DIR = './output_tsvs'  # 导出文件目录
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. 读取需要的簡稱列表
df_need = pd.read_excel(EXCEL_PATH)
needed_abbrs = df_need['need'].dropna().astype(str).unique()

# 2. 开始按需查询并导出
conn = sqlite3.connect(DIALECTS_DB_PATH)
for abbr in needed_abbrs:
    query = """
    SELECT 漢字, 音節, 註釋
    FROM dialects
    WHERE 簡稱 = ?
    """
    chunk_df = pd.read_sql_query(query, conn, params=(abbr,))

    if chunk_df.empty:
        continue

    chunk_df.columns = ['#漢字', '音標', '解釋']

    # 导出到 TSV
    output_path = os.path.join(OUTPUT_DIR, f"{abbr}.tsv")
    chunk_df.to_csv(output_path, sep='\t', index=False, encoding='utf-8')

conn.close()

print("TSV 导出完毕")