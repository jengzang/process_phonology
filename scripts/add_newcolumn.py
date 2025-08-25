import sqlite3

from common.config import SUPPLE_DB_PATH, USER_DATABASE_PATH


def add_columns_to_api_usage_logs(db_path):
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 检查表的结构，确保这些列不存在
        cursor.execute("PRAGMA table_info(api_usage_logs);")
        columns = [column[1] for column in cursor.fetchall()]

        # 如果没有 request_size 和 response_size 列，则添加它们
        # if 'total_upload' not in columns:
        #     cursor.execute("ALTER TABLE api_usage_summary ADD COLUMN total_upload INTEGER DEFAULT 0;")
        #     print("Added 'request_size' column.")

        if 'total_duration' not in columns:
            cursor.execute("ALTER TABLE api_usage_summary ADD COLUMN total_duration INTEGER DEFAULT 0;")
            print("Added 'response_size' column.")

        # 提交更改并关闭连接
        conn.commit()
        conn.close()

        print("Columns added successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")


# 替换为你的数据库文件路径
db_path = USER_DATABASE_PATH
add_columns_to_api_usage_logs(db_path)
