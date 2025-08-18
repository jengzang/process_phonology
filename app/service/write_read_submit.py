import os
import re
import sqlite3

from common.getloc_by_name_region import query_dialect_abbreviations
from common.config import SUPPLE_DB_PATH


# 处理表单提交的函数
def handle_form_submission(form_data):
    # 确保数据库已经初始化
    def init_db():
        # 确保数据库已经初始化并且表已经创建
        if not os.path.exists(SUPPLE_DB_PATH):
            print("Database file does not exist. Creating new one...")

        conn = sqlite3.connect(SUPPLE_DB_PATH)
        cursor = conn.cursor()

        # 确保 'informations' 表存在，如果不存在则创建
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS informations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                簡稱 TEXT NOT NULL,
                音典分區 TEXT NOT NULL,
                經緯度 TEXT NOT NULL,
                特徵 TEXT NOT NULL,
                值 TEXT NOT NULL,
                說明 TEXT,
                存儲標記 INTEGER NOT NULL DEFAULT 1,
                maxValue TEXT NOT NULL  -- 添加 maxValue 字段
            )
        ''')
        conn.commit()
        conn.close()
        print("Database initialized (or already exists).")  # 调试输出

    init_db()

    # 取得表單數據
    location = form_data.get('location')
    region = form_data.get('region')
    coordinates = form_data.get('coordinates')
    feature = form_data.get('feature')
    value = form_data.get('value')
    description = form_data.get('description', None)

    print(
        f"Received form data: location={location}, region={region}, coordinates={coordinates}, feature={feature}, value={value}, description={description}")  # Debug output

    # 檢查必要字段是否為空
    if not location or not region or not coordinates or not feature or not value:
        print("Error: Missing required fields!")  # Debug output
        return {"success": False, "message": "所有字段（除說明）必須填寫！"}

    def get_max_value(value: str):
        # 去除空格
        value = value.strip()

        # 1. 如果没有括号、逗号或斜杠
        if '(' not in value and ',' not in value and '/' not in value:
            return value

        # 2. 如果没有括号，但有逗号或斜杠
        if '(' not in value and (',' in value or '/' in value):
            # 提取逗号或斜杠之前的部分
            return re.split('[,/]', value)[0]

        # 3. 如果有括号，但没有逗号或斜杠
        if '(' in value and ',' not in value and '/' not in value:
            # 去掉星号并提取括号中的内容
            value_inside_parentheses = re.search(r'\((.*?)\)', value)
            if value_inside_parentheses:
                return value_inside_parentheses.group(1).replace('*', '')

        # 4. 如果有括号并且有逗号或斜杠
        if '(' in value and (',' in value or '/' in value):
            # 去掉括号部分并提取逗号或斜杠之前的部分
            value_without_parentheses = re.sub(r'\(.*?\)', '', value)
            return re.split('[,/]', value_without_parentheses)[0]

        # 5. 如果有括号，但括号外有字符
        if '(' in value:
            # 提取括号外的部分
            value_outside_parentheses = re.sub(r'\(.*?\)', '', value)

            # 如果括号外有字符，并且没有逗号或斜杠，优先取括号外的字符
            if value_outside_parentheses and (',' not in value and '/' not in value):
                return value_outside_parentheses.strip()

            # 如果有逗号或斜杠，取括号外的部分，从第一个字符到第一个逗号或斜杠之间的字符
            return re.split('[,/]', value_outside_parentheses)[0]

    # 计算 maxValue
    max_value = get_max_value(value)  # 计算 maxValue

    # 將數據插入資料庫
    try:
        print("Connecting to the database for insertion...")  # Debug output
        conn = sqlite3.connect(SUPPLE_DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO informations (簡稱, 音典分區, 經緯度, 特徵, 值, 說明, 存儲標記, maxValue)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (location, region, coordinates, feature, value, description, 1, max_value))  # 1 for the storage flag

        print("Executing insertion query...")  # Debug output
        conn.commit()
        conn.close()

        print("Data inserted successfully.")  # Debug output
        return {"success": True, "message": "數據提交成功！"}

    except Exception as e:
        print(f"Error: {str(e)}")  # Debug output
        return {"success": False, "message": f"提交失敗：{str(e)}"}


def get_from_submission(locations, regions, need_features):
    # 获取all_locations
    all_locations = query_dialect_abbreviations(regions, locations, db_path=SUPPLE_DB_PATH, tables="informations")

    # 连接到数据库
    conn = sqlite3.connect(SUPPLE_DB_PATH)
    cursor = conn.cursor()

    # 创建一个空的列表来存储结果
    result = []

    for location in all_locations:
        for feature in need_features:
            # 构造查询条件，增加查询 "maxValue"
            query = f"""
            SELECT "簡稱", "特徵", "值", "經緯度", "說明", "maxValue"
            FROM informations
            WHERE "簡稱" = ? AND "特徵" = ?
            """
            cursor.execute(query, (location, feature))

            # 获取查询结果
            rows = cursor.fetchall()

            # 如果查询有结果，处理并添加到结果列表
            for row in rows:
                # 解析經緯度，将字符串 "40.7128, -74.0060" 转换为列表 [40.7128, -74.0060]
                latitude_longitude = list(map(float, re.split(r'[，,]', row[3])))

                result.append({
                    "簡稱": row[0],
                    "特徵": row[1],
                    "值": row[2],
                    "maxValue": row[5],  # 直接从数据库中获取 maxValue
                    "經緯度": latitude_longitude,
                    "說明": row[4]
                })

    # 关闭数据库连接
    conn.close()

    # 返回所有匹配到的结果
    return result

