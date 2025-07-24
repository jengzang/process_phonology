import os
import re
import sqlite3
from typing import Union, List

import numpy as np

from source.config import QUERY_DB_PATH, SUPPLE_DB_PATH, DIALECTS_DB_PATH, CHARACTERS_DB_PATH

import sqlite3
import os
from typing import Union, List

from source.format_convert import s2t_pro
from source.process_input import query_dialect_abbreviations


def fetch_dialect_region(input_data: Union[str, List[str]]) -> dict:
    if isinstance(input_data, list):
        query_str = input_data[0]  # 取數組的第一個元素
    else:
        query_str = input_data  # 如果是字符串，直接使用它

    # 連接資料庫並查詢
    conn = sqlite3.connect(QUERY_DB_PATH)
    cursor = conn.cursor()

    print(f"Executing query to fetch dialect region for: {query_str}")  # Debug output

    cursor.execute("SELECT 音典分區 FROM dialects WHERE 簡稱 = ?", (query_str,))
    result = cursor.fetchone()

    conn.close()

    # 如果找到結果，返回音典分區；否則返回錯誤消息
    if result:
        return {"音典分區": result[0]}
    else:
        return {"error": "未找到對應的音典分區"}


# 计算 maxValue 的函数
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
                latitude_longitude = list(map(float, row[3].split(',')))

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



import sqlite3
import os

import sqlite3
import os

def search_characters(chars, locations=None, regions=None):
    # 假设 query_dialect_abbreviations 函数返回一个地点简称的列表
    all_locations = query_dialect_abbreviations(regions, locations)

    # 确保 chars 是一个字符列表
    if isinstance(chars, str):
        chars = list(chars)  # 如果是字符串，转换成字符列表
    elif isinstance(chars, (list, np.ndarray)):
        # 如果是嵌套列表或数组，进行扁平化处理
        chars = [char for sublist in chars for char in
                 (sublist if isinstance(sublist, (list, np.ndarray)) else [sublist])]

    # 调用 s2t_pro 函数进行字符转换
    clean_str, _ = s2t_pro(chars, level=2)  # 调用 s2t_pro 进行转换

    # 输出列表
    result = []

    # 连接到方言数据库和字符数据库，设置 row_factory 为 sqlite3.Row
    dialect_conn = sqlite3.connect(DIALECTS_DB_PATH)
    dialect_conn.row_factory = sqlite3.Row  # 使查询结果返回字典
    characters_conn = sqlite3.connect(CHARACTERS_DB_PATH)
    characters_conn.row_factory = sqlite3.Row  # 使查询结果返回字典

    for char in clean_str:
        for location in all_locations:  # 对每个字和每个地点进行查询
            # 查询方言数据库（dialects表），确保获取到地点简称
            dialect_cursor = dialect_conn.cursor()
            dialect_query = """
                SELECT 音節, 多音字, 註釋, 簡稱
                FROM dialects
                WHERE 漢字 = ? AND 簡稱 = ?
            """
            dialect_cursor.execute(dialect_query, [char, location])
            dialect_results = dialect_cursor.fetchall()

            syllables = []  # 用于存储音节列表
            notes = []  # 用于存储註釋列表
            for row in dialect_results:
                syllables.append(row['音節'])  # 记录音节
                if row['註釋']:  # 如果註釋列不为空
                    notes.append(row['註釋'])  # 将註釋添加到 notes 列表中
            syllables = list(set(syllables))  # 去重音节列表，防止重复
            notes = list(set(notes))  # 去重註釋列表

            # 如果是多音字，则遍历整个表查找该字的其他音节
            if len(syllables) == 1 and row['多音字'] == 1:
                # 字是多音字，遍历整个表查找音节
                syllables = []
                all_syllables_cursor = dialect_conn.cursor()
                all_syllables_query = """
                    SELECT 音節, 註釋
                    FROM dialects
                    WHERE 漢字 = ?
                """
                all_syllables_cursor.execute(all_syllables_query, [char])
                all_syllables_results = all_syllables_cursor.fetchall()
                for syllable_row in all_syllables_results:
                    syllables.append(syllable_row['音節'])
                    if syllable_row['註釋']:  # 如果該音節有註釋
                        notes.append(syllable_row['註釋'])
                syllables = list(set(syllables))  # 去重音节列表
                notes = list(set(notes))  # 去重註釋列表

            # 对于多音字，合并音节的註釋
            if len(syllables) > 1:
                notes = "; ".join(notes)  # 如果有多个音节且都有註釋，用分号连接

            # 为每个字和地点配对
            result.append({
                'char': char,
                '音节': syllables,
                'location': location,
                'positions': [],  # 初始化，后面会填充
                'notes': notes  # 添加註釋
            })

            # 查询字符数据库（characters表）
            characters_cursor = characters_conn.cursor()
            characters_query = """
                SELECT 攝, 呼, 等, 韻, 調, 組, 聲, 多地位標記
                FROM characters
                WHERE 漢字 = ?
            """
            characters_cursor.execute(characters_query, [char])
            characters_results = characters_cursor.fetchall()

            positions = []  # 用于存储所有的地位信息
            for row in characters_results:
                # 拼接 parts 和 meta
                parts = f"{row['攝']}{row['呼']}{row['等']}{row['韻']}{row['調']}"
                meta = f"{row['組']}「組」{row['聲']}「母」"

                # 拼接后的地位
                if row['多地位標記'] == 1:  # 如果有多地位标记
                    # 查找与当前字相同且有多地位标记的所有字
                    position_cursor = characters_conn.cursor()
                    position_query = """
                        SELECT 漢字, 攝, 呼, 等, 韻, 調, 組, 聲
                        FROM characters
                        WHERE 多地位標記 = 1 AND 漢字 = ?
                    """
                    position_cursor.execute(position_query, [char])
                    position_results = position_cursor.fetchall()

                    # 将所有找到的地位信息添加到 positions 中
                    for position_row in position_results:
                        position_parts = f"{position_row['攝']}{position_row['呼']}{position_row['等']}{position_row['韻']}{position_row['調']}"
                        position_meta = f"{position_row['組']}「組」{position_row['聲']}「母」"
                        positions.append(f"{position_parts},{position_meta}")
                else:
                    # 非多地位字，直接添加其地位信息
                    positions.append(f"{parts},{meta}")

            # 保存所有的地位
            result[-1]['positions'] = positions

    # 关闭数据库连接
    dialect_conn.close()
    characters_conn.close()

    return result



locations = ["東莞莞城", "雲浮富林"]
chars = "干"
result = search_characters(chars, locations)
print(result)
