import sqlite3
from collections import defaultdict

from common.config import CHARACTERS_DB_PATH

# ✅ 替換成你的實際 SQLite 檔案路徑
db_file = CHARACTERS_DB_PATH

# 要提取的欄位
fields = [
    "攝", "呼", "等", "韻", "入", "調", "清濁",
    "系", "組", "母", "部位", "方式"
]

# 建立字典來儲存唯一值
column_values = defaultdict(set)

# 連接資料庫
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# 逐欄查詢唯一值
for col in fields:
    try:
        cursor.execute(f"SELECT DISTINCT {col} FROM characters WHERE {col} IS NOT NULL")
        results = cursor.fetchall()
        for row in results:
            val = row[0].strip()
            if val:
                column_values[col].add(val)
    except Exception as e:
        print(f"❌ 欄位 {col} 查詢失敗: {e}")

conn.close()

# 將 set 轉成排序好的 list
column_values = {k: sorted(v) for k, v in column_values.items()}

# ✅ 印出結果（像你那樣）
import pprint
pprint.pprint(column_values, width=120)
