import os
import re
import sqlite3
from difflib import SequenceMatcher
from typing import Union, List

import numpy as np
import pandas as pd
from opencc import OpenCC
from pypinyin import lazy_pinyin

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

    # 連接資料庫並查詢
    # 連接資料庫並查詢
    def query_database(db_path: str, table_name: str) -> tuple:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        query = f"SELECT 音典分區 FROM {table_name} WHERE 簡稱 = ?"
        cursor.execute(query, (query_str,))
        result = cursor.fetchone()
        conn.close()
        return result

    # 首先查詢主資料庫的表
    result = query_database(QUERY_DB_PATH, 'dialects')  # 假設主資料庫表名為 'dialects'

    # 如果在主資料庫中找不到結果，則查詢補充資料庫的表
    if not result:
        result = query_database(SUPPLE_DB_PATH, 'informations')  # 假設補充資料庫表名為 'informations'

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


def search_tones(locations=None, regions=None, get_raw: bool = False):
    # 假设 query_dialect_abbreviations 函数返回一个地点简称的列表
    all_locations = query_dialect_abbreviations(regions, locations)

    # 打开数据库连接
    conn = sqlite3.connect(QUERY_DB_PATH)
    cursor = conn.cursor()

    # 查询dialects表的相关列
    query = """
    SELECT 簡稱, T1陰平, T2陽平, T3陰上, T4陽上, T5陰去, T6陽去, T7陰入, T8陽入, T9其他調, T10輕聲 FROM dialects
    """
    # 使用pandas读取数据
    df = pd.read_sql(query, conn)

    # 设置簡稱为索引
    df.set_index('簡稱', inplace=True)

    # 如果传入了abbreviation，则根据它过滤数据
    if all_locations is not None:
        df = df.loc[all_locations]

    # 处理每一列的单元格
    def process_cell(value, num):
        # 如果值是 None 或 NaN，返回空字符串
        if value is None or pd.isnull(value):
            return ""
        if isinstance(value, str):  # 确保是字符串
            # 如果没有 []，在开头添加[num]
            if ('[' not in value) or (']' not in value):
                return f"[{num}]{value}"
            else:
                # 如果有 []，按逗号拆分并处理
                elements = re.split(r'[，,|;]', value)
                processed_elements = []
                for element in elements:
                    # 只有当元素没有 [num] 或 [] 时才加上[num]
                    if '[' not in element and ']' not in element:
                        processed_elements.append(f"[{num}]{element}")
                    else:
                        processed_elements.append(element)
                return ','.join(processed_elements)
        return value

    match_table = {
        'T1': ['陰平', '平聲', '阴平', '平声'],
        'T2': ['陽平', '阳平'],
        'T3': ['陰上', '上聲', '阴上', '上声'],
        'T4': ['陽上', '阳上'],
        'T5': ['陰去', '去聲', '阴去', '去声'],
        'T6': ['陽去', '阳去'],
        'T7': ['陰入', '阴入'],
        'T8': ['陽入', '阳入']
    }

    # 遍历数据框并进行处理
    for col_num, col_name in enumerate(df.columns, start=1):
        # 处理每一列的每一行
        df[col_name] = df[col_name].apply(lambda x: process_cell(x, col_num))

    result = []
    new_result = []

    # 遍历所有数据行
    for index, row in df.iterrows():
        # 获取总数据
        total_data = [str(x) if x != "" else "" for x in row.tolist()]

        # 创建一个字典，保留簡稱和總數據
        row_data = {
            "簡稱": index,
            "總數據": total_data
        }

        # 生成新的 tones 字段
        new_row = {
            "簡稱": index,
            "總數據": total_data,
            "tones": []
        }

        # Part 1: 循环处理 T1 到 T8
        for i in range(1, 9):  # 范围是 1 到 8（包含 8）
            matched = total_data[i - 1]  # 索引从 0 开始，因此使用 i - 1

            # 去除方括号和其中的内容
            raw_value = re.sub(r'\[.*?\]', '', matched)  # 删除方括号和其中的内容

            if raw_value:
                # 按逗号分割
                raw_parts = re.split(r'[，,]', raw_value)
                value_list = []
                name_list = []

                for part in raw_parts:
                    # 提取数字部分 (value)
                    value = ''.join(re.findall(r'\d+', part))
                    # 提取汉字部分 (name)
                    name = ''.join(re.findall(r'[^\d,]+', part))

                    # 如果 name 中包含 "入"，则给 value 添加前缀
                    if "入" in name:
                        value = f'`{value}'  # 给 value 添加前缀

                    value_list.append(value)
                    name_list.append(name)

                # 匹配名称
                match_list = []
                for name in name_list:
                    matched_t = set()  # 使用 set 来去重
                    for t, names in match_table.items():
                        if any(matching_name in name for matching_name in names):  # 部分匹配
                            matched_t.add(t)

                    match_list.extend(list(matched_t))  # 将 set 转回 list，直接扩展到 match_list
                    # 如果 T5 没有被匹配到，则使用备用规则 ['去'] 来匹配 T5
                    if 'T1' not in match_list:
                        if '平' in name and not re.search(r'^(陽|阳)', name):
                            match_list.append('T1')
                    if 'T3' not in match_list:
                        if '上' in name and not re.search(r'^(陽|阳)', name):
                            match_list.append('T3')
                    if 'T5' not in match_list:
                        if '去' in name and not re.search(r'^(陽|阳)', name):
                            match_list.append('T5')
                    if 'T7' not in match_list:
                        if '入' in name and not re.search(r'^(陽|阳)', name):
                            match_list.append('T7')

                # 去重 match_list
                match_list = list(set(match_list))
                bracket_nums = re.findall(r'\[(\d+)\]', matched)

                # 将结果保存到 row_data 字典中
                row_data[f"T{i}"] = {
                    'raw': raw_value,
                    'value': value_list,
                    'name': name_list,
                    'match': match_list,
                    'num': bracket_nums
                }

                # 更新 tones 列表
                new_row['tones'].append(
                    {f"T{i}": ','.join(value_list) if value_list else ','.join(match_list) if match_list else '無'})
            else:
                # 如果没有匹配值，初始化为空
                row_data[f"T{i}"] = {
                    'raw': '',
                    'value': [],
                    'name': [],
                    'match': [],
                    'num': []
                }

                new_row['tones'].append({f"T{i}": '無'})  # 初步处理为无匹配

        # Part 2: 循环处理 T9 到 T10
        for i in range(9, 11):  # 范围是 9 到 10（包含 10）
            matched = total_data[i - 1]  # 索引从 0 开始，因此使用 i - 1

            # 去除方括号和其中的内容
            raw_value = re.sub(r'\[.*?\]', '', matched)  # 删除方括号和其中的内容

            if raw_value:
                # 按逗号分割
                raw_parts = re.split(r'[，,]', raw_value)
                value_list = []
                name_list = []

                for part in raw_parts:
                    # 提取数字部分 (value)
                    value = ''.join(re.findall(r'\d+', part))
                    # 提取汉字部分 (name)
                    name = ''.join(re.findall(r'[^\d,]+', part))

                    # 如果 name 中包含 "入"，则给 value 添加前缀
                    if "入" in name:
                        value = f'`{value}'  # 给 value 添加前缀

                    value_list.append(value)
                    name_list.append(name)

                # 匹配名称
                match_list = []
                for name in name_list:
                    matched_t = set()  # 使用 set 来去重
                    for t, names in match_table.items():
                        if any(matching_name in name for matching_name in names):  # 部分匹配
                            matched_t.add(t)

                    match_list.extend(list(matched_t))  # 将 set 转回 list，直接扩展到 match_list

                # 去重 match_list
                match_list = list(set(match_list))
                bracket_nums = re.findall(r'\[(\d+)\]', matched)

                # 将结果保存到 row_data 字典中
                row_data[f"T{i}"] = {
                    'raw': raw_value,
                    'value': value_list,
                    'name': name_list,
                    'match': match_list,
                    'num': bracket_nums
                }

                # 更新 tones 列表
                new_row['tones'].append(
                    {f"T{i}": ','.join(value_list) if value_list else ','.join(match_list) if match_list else '無'})
            else:
                # 如果没有匹配值，初始化为空
                row_data[f"T{i}"] = {
                    'raw': '',
                    'value': [],
                    'name': [],
                    'match': [],
                    'num': []
                }

                new_row['tones'].append({f"T{i}": '無'})  # 初步处理为无匹配

        # 在这里遍历结束之后再处理没有匹配的 T
        for i in range(1, 11):  # 再次遍历每个 T
            t_data = row_data[f"T{i}"]

            if not t_data['value']:  # 如果 T[i] 的 value 为空
                match_found = []
                for j in range(1, 11):  # 遍历同一簡稱中的其他 T（T1 到 T10）
                    if j != i:  # 避免比较自己
                        t_j_data = row_data[f"T{j}"]
                        if f"T{i}" in t_j_data.get('match', []):  # 检查 T[i] 是否在 T[j] 的 match 中
                            match_found.append(f"T{j}")  # 如果匹配，则加入匹配列表

                # 打印调试输出：当前 T[i] 在其它 T 的 match 中找到了什么
                # print(f"Searching for matches for T{i}: Found {match_found}")

                if match_found:
                    row_data[f"T{i}"]['match'] = ','.join(match_found)  # 填充匹配的 T
                    new_row['tones'][i - 1] = {f"T{i}": ','.join(match_found)}  # 更新 tones
                else:
                    row_data[f"T{i}"]['match'] = '無'  # 如果没有匹配项，填充无
                    new_row['tones'][i - 1] = {f"T{i}": '無'}  # 更新 tones 为无

        # 添加到 result 和 new_result 中
        if get_raw:
            result.append(row_data)
            return result
        new_result.append(new_row)

    return new_result


def match_custom_feature(locations, regions, keyword):
    opencc_t2s = OpenCC('t2s')
    # 候選集初始化
    candidate_set = set()
    candidate_set.add(keyword)

    # 繁體 → 簡體
    try:
        simp = opencc_t2s.convert(keyword)
        candidate_set.add(simp)
    except:
        pass

    # 簡體 → 繁體候選（多對一）
    try:
        trad_string, trad_map = s2t_pro(keyword, level=2)
        candidate_set.add(trad_string)
        for _, 候選列表 in trad_map:
            candidate_set.update(候選列表)
    except:
        pass

    # 拼音比對預備
    word_pinyin = ''.join(lazy_pinyin(keyword))

    # 查詢資料庫位置
    all_locations = query_dialect_abbreviations(
        regions, locations, db_path=SUPPLE_DB_PATH, tables="informations"
    )
    # print(all_locations)
    conn = sqlite3.connect(SUPPLE_DB_PATH)
    cursor = conn.cursor()
    result = []

    for location in all_locations:
        cursor.execute("""
               SELECT "簡稱", "特徵"
               FROM informations
               WHERE "簡稱" = ?
           """, (location,))
        rows = cursor.fetchall()

        for row in rows:
            特徵 = row[1]

            # 直接或轉換字匹配
            if any(c in 特徵 for c in candidate_set):
                result.append({
                    "簡稱": row[0],
                    "特徵": 特徵
                })
                continue

            # 拼音模糊比對
            特徵_pinyin = ''.join(lazy_pinyin(特徵))
            ratio = SequenceMatcher(None, word_pinyin, 特徵_pinyin).ratio()
            if ratio > 0.7:
                result.append({
                    "簡稱": row[0],
                    "特徵": 特徵
                })

    conn.close()
    return result


# result = process_dialect_data()
# print(result)
# locations = ['南寧五塘']
# # # chars = ['干']
# result = search_tones(locations)
# print(result)
# results = match_custom_feature(
#     locations=[],
#     regions=["嶺南"],
#     keyword="lai"
# )
#
# for r in results:
#     print(r)
