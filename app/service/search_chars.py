import numpy as np

from common.config import DIALECTS_DB_PATH, CHARACTERS_DB_PATH

import sqlite3

from common.s2t import s2t_pro
from common.getloc_by_name_region import query_dialect_abbreviations


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
    clean_str, _ = s2t_pro(chars, level=2)

    # 输出列表
    result = []

    # 连接到方言数据库和字符数据库，设置 row_factory 为 sqlite3.Row
    dialect_conn = sqlite3.connect(DIALECTS_DB_PATH)
    dialect_conn.row_factory = sqlite3.Row  # 使查询结果返回字典
    characters_conn = sqlite3.connect(CHARACTERS_DB_PATH)
    characters_conn.row_factory = sqlite3.Row  # 使查询结果返回字典

    try:
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

                # ======== 最小化改動：確保音節與註釋一一對應（開始） ========
                # 用 音節 -> 註釋集合 聚合，並以旗標判斷是否多音
                syllable2notes = {}  # { '音節': set([...]) }
                is_polyphonic = False

                for r in dialect_results:
                    syl = r['音節']
                    note = (r['註釋'] or '').strip()
                    if r['多音字'] == 1:
                        is_polyphonic = True
                    if syl not in syllable2notes:
                        syllable2notes[syl] = set()
                    if note:
                        syllable2notes[syl].add(note)

                # 若判定為多音字且目前只抓到一個音節，補抓該字在所有記錄中的音節/註釋
                if is_polyphonic and len(syllable2notes) <= 1:
                    all_syllables_cursor = dialect_conn.cursor()
                    all_syllables_query = """
                        SELECT 音節, 註釋
                        FROM dialects
                        WHERE 漢字 = ?
                    """
                    all_syllables_cursor.execute(all_syllables_query, [char])
                    all_syllables_results = all_syllables_cursor.fetchall()
                    for rr in all_syllables_results:
                        syl = rr['音節']
                        note = (rr['註釋'] or '').strip()
                        if syl not in syllable2notes:
                            syllable2notes[syl] = set()
                        if note:
                            syllable2notes[syl].add(note)

                # 產出與原結構相容的 list，索引一一對應
                # （為了最小改動，不引入新欄位；如需固定排序可改為 sorted(syllable2notes)）
                syllables = list(syllable2notes.keys())
                notes = ['; '.join(sorted(syllable2notes[syl])) if syllable2notes[syl] else '_'
                         for syl in syllables]

                # ======== 最小化改動：確保音節與註釋一一對應（結束） ========

                # 为每个字和地点配对
                result.append({
                    'char': char,
                    '音节': syllables,  # 與 notes 一一對應
                    'location': location,
                    'positions': [],  # 初始化，后面会填充
                    'notes': notes  # 現在是 list，與音節對齊
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

    finally:
        # 关闭数据库连接
        dialect_conn.close()
        characters_conn.close()

    return result


