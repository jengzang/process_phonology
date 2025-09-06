import sqlite3
from common.config import SUPPLE_DB_PATH, DIALECTS_DB_ADMIN, DIALECTS_DB_PATH, DIALECTS_DB_USER, QUERY_DB_USER, \
    QUERY_DB_ADMIN, QUERY_DB_PATH, CHARACTERS_DB_PATH

# 指定資料庫路徑
db_path = r"C:\Users\joengzaang\PycharmProjects\chars\data\characters.db"  # 替換成實際路徑

# # 建立資料庫連線
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
#
# # 定義要建立的索引（避免重複建立時出錯）
# index_statements = [
#     "CREATE INDEX IF NOT EXISTS idx_informations_abbr ON informations(簡稱);",
#     "CREATE INDEX IF NOT EXISTS idx_informations_partition ON informations(音典分區);",
#     "CREATE INDEX IF NOT EXISTS idx_informations_user ON informations(user_id);",
#     "CREATE INDEX IF NOT EXISTS idx_informations_created_at ON informations(created_at);",
#     "CREATE INDEX IF NOT EXISTS idx_informations_flag ON informations(存儲標記);"
# ]
#
# # 執行每一條 SQL 建立索引
# for stmt in index_statements:
#     cursor.execute(stmt)
# 查询所有显式创建的索引
cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL;")
indexes = cursor.fetchall()

if indexes:
    print("已存在索引：")
    for name, sql in indexes:
        print(f"- 索引名稱: {name}")
        print(f"  建立語法: {sql}")
else:
    print("⚠️ 沒有找到任何索引。")

# ✅ 查詢 characters 表的總行數
cursor.execute("SELECT COUNT(*) FROM characters;")
row_count = cursor.fetchone()[0]
print(f"\n📊 characters 表行數：{row_count} 行")

# 提交變更並關閉連線
conn.commit()
conn.close()

# print("✅ 索引已建立完成。")
