import math
import os
import re
import sqlite3
from collections import defaultdict
from itertools import product
from typing import Tuple, Union, List, Optional

import Levenshtein
from pypinyin import lazy_pinyin

from source.config import QUERY_DB_PATH, SUPPLE_DB_PATH
from source.format_convert import s2t_pro

# 可用於分層篩選的欄位
HIERARCHY_COLUMNS = ["攝", "呼", "等", "韻", "入", "調", "清濁", "系", "組", "聲"]
# 硬編碼值表
column_values = {
    "攝": ['假', '咸', '宕', '山', '效', '曾', '果', '梗', '止', '江', '流', '深', '臻', '蟹', '通', '遇'],
    "呼": ['合', '開'],
    "等": ['一', '三', '二', '四'],
    "韻": ['之', '仙', '佳', '侯', '侵', '元', '先', '冬', '凡', '刪', '咍', '咸', '唐', '嚴', '夬', '宵', '寒',
           '尤', '山', '幽', '庚', '廢', '微', '支', '文', '東', '桓', '模', '欣', '歌', '江', '泰', '添', '清',
           '灰', '痕', '登', '皆', '真', '祭', '耕', '肴', '脂', '臻', '蒸', '蕭', '虞', '覃', '談', '豪', '銜',
           '鐘', '陽', '青', '魂', '魚', '鹽', '麻', '齊'],
    "入": ['入', '舒'],
    "調": ['上', '入', '去', '平'],
    "清濁": ['全清', '全濁', '次清', '次濁', '清', '濁'],
    "系": ['幫', '知', '端', '見'],
    "組": ['幫', '影', '日', '曉', '泥', '知', '章', '端', '精', '莊', '見', '非'],
    "聲": ['並', '云', '以', '來', '初', '匣', '奉', '娘', '定', '崇', '常', '幫', '影', '從', '微', '徹', '心',
           '敷', '日', '昌', '明', '曉', '書', '泥', '清', '溪', '滂', '澄', '生', '疑', '知', '禪', '章', '端',
           '精', '群', '船', '莊', '見', '透', '邪', '非']
}


# # 優先邏輯（分層關係）
# priority = [
#     ("聲", ["聲", "組", "系"]),
#     ("攝", ["攝", "韻"]),
#     ("調", ["入", "調"]),
#     ("清濁", ["清濁"]),
#     ("等", ["等"]),
#     ("呼", ["呼"]),
# ]


def match_locations(user_input, filter_valid_abbrs_only=True):
    def is_pinyin_similar(a, b):
        if not a or not b:
            return False
        return lazy_pinyin(a) == lazy_pinyin(b)

    def is_similar(a, b, threshold=0.7):
        if not a or not b:
            return False
        max_len = max(len(a), len(b))
        return 1 - Levenshtein.distance(a, b) / max_len >= threshold

    # print(f"[DEBUG] 使用者輸入：{user_input}")

    def generate_strict_candidates(mapping, input_len):
        # 每個位置逐字取候選值組合（不產生交叉混用）
        combinations = [[]]
        for _, candidates in mapping:
            new_combos = []
            for combo in combinations:
                for c in candidates:
                    new_combos.append(combo + [c])
            combinations = new_combos
        # 合併成詞，保證長度一致
        return {''.join(chars) for chars in combinations if len(chars) == input_len}

    # 使用 s2t_pro 轉換
    converted_str, mapping = s2t_pro(user_input, level=2)
    input_len = len(user_input)

    # 安全構造詞組候選集
    converted_candidates = generate_strict_candidates(mapping, input_len)

    # possible_inputs 包含：
    # - 原輸入
    # - 轉換字詞（保證不交叉）
    # - clean_str（第一候選組合）
    possible_inputs = set([user_input, converted_str]) | converted_candidates

    conn = sqlite3.connect(QUERY_DB_PATH)
    cursor = conn.cursor()

    # 根據 filter_valid_abbrs_only 決定是否過濾掉非存儲標記為1的數據

    if filter_valid_abbrs_only:
        # print("過濾！！")
        cursor.execute("SELECT 簡稱 FROM dialects WHERE 存儲標記 = 1")
    else:
        # print("不過濾存儲標記")
        cursor.execute("SELECT 簡稱 FROM dialects")
    valid_abbrs_set = set(row[0] for row in cursor.fetchall())

    matched_abbrs = set()
    for term in possible_inputs:
        # 完全匹配查詢部分需要根據 filter_valid_abbrs_only 來過濾
        if filter_valid_abbrs_only:
            cursor.execute("SELECT 簡稱 FROM dialects WHERE 簡稱 = ? AND 存儲標記 = 1", (term,))
        else:
            cursor.execute("SELECT 簡稱 FROM dialects WHERE 簡稱 = ?", (term,))
        exact = cursor.fetchall()
        matched_abbrs.update([row[0] for row in exact])
        # print(f"[DEBUG] 完全匹配【{term}】：{exact}")

    if matched_abbrs:
        return list(matched_abbrs), 1, [], [], [], [], [], []

    fuzzy_abbrs = set()
    for term in possible_inputs:
        # 模糊匹配查詢部分需要根據 filter_valid_abbrs_only 來過濾
        if filter_valid_abbrs_only:
            cursor.execute("SELECT 簡稱 FROM dialects WHERE 簡稱 LIKE ? AND 存儲標記 = 1", (term + "%",))
        else:
            cursor.execute("SELECT 簡稱 FROM dialects WHERE 簡稱 LIKE ?", (term + "%",))
        fuzzy = cursor.fetchall()
        fuzzy_abbrs.update([row[0] for row in fuzzy])
        # print(f"[DEBUG] 模糊簡稱匹配【{term}】：{fuzzy}")

    geo_matches = set()
    geo_abbr_map = {}
    all_geo_names = []
    all_abbr_names = []

    for col in ["鎮", "行政村", "自然村"]:
        if filter_valid_abbrs_only:
            cursor.execute(f"SELECT {col}, 簡稱 FROM dialects WHERE 存儲標記 = 1")
        else:
            cursor.execute(f"SELECT {col}, 簡稱 FROM dialects")
        rows = cursor.fetchall()
        for name, abbr in rows:
            all_geo_names.append(name)
            all_abbr_names.append(abbr)
            for term in possible_inputs:
                if term in (name or ""):
                    geo_matches.add(name)
                    geo_abbr_map[name] = abbr

    # 加上所有簡稱（用於相似與拼音匹配）
    all_names = all_geo_names + list(valid_abbrs_set)
    all_abbrs = all_abbr_names + list(valid_abbrs_set)

    fuzzy_geo_matches = set()
    fuzzy_geo_abbrs = set()
    sound_like_matches = set()
    sound_like_abbrs = set()

    for name, abbr in zip(all_names, all_abbrs):
        if not name or not abbr or abbr not in valid_abbrs_set:
            continue

        if is_similar(user_input, name):
            # print(f"[DEBUG] 相似匹配: '{user_input}' ≈ '{name}' (abbr: {abbr})")
            fuzzy_geo_matches.add(name)
            fuzzy_geo_abbrs.add(abbr)

        if is_pinyin_similar(user_input, name):
            # print(f"[DEBUG] 拼音匹配: '{user_input}' ≈ '{name}' (abbr: {abbr})")
            sound_like_matches.add(name)
            sound_like_abbrs.add(abbr)

    return (
        list(fuzzy_abbrs),
        0,
        list(geo_matches),
        [geo_abbr_map[n] for n in geo_matches if geo_abbr_map[n] in valid_abbrs_set],
        list(fuzzy_geo_matches),
        list(fuzzy_geo_abbrs),
        list(sound_like_matches),
        list(sound_like_abbrs),
    )


def match_locations_batch(input_string: str, filter_valid_abbrs_only=True):
    input_string = input_string.strip()
    if not input_string:
        print("⚠️ 輸入為空，無法處理。")
        return []

    # 以多種分隔符切分
    parts = re.split(r"[ ,;/，；、]+", input_string)
    results = []

    for idx, part in enumerate(parts):
        part = part.strip()
        if part:
            # print(f"\n🔹 處理第 {idx + 1} 個地名：{part}")
            try:
                res = match_locations(part, filter_valid_abbrs_only)
                print(f"   ⮡ 結果: {res}")
                results.append(res)
            except Exception as e:
                print(f"   ❌ 發生錯誤：{e}")
                results.append((False, 0, [], [], [], [], [], []))

    return results


def auto_convert_single(user_input: str) -> Union[Tuple[str, int], Tuple[bool, int]]:
    def process(input_text: str, priority_key: Optional[str] = None) -> Union[Tuple[str, int], Tuple[bool, int]]:
        result = []
        match_count = 0
        used_columns = set()
        i = 0
        pending_clear = []

        extended_column_values = column_values.copy()
        extended_column_values["聲"] = column_values["聲"] + ["@清"]
        extended_column_values["韻"] = column_values["韻"] + ["#清"]
        extended_column_values["清濁"] = column_values["清濁"] + ["*清"]

        value_to_columns = {}
        for col, values in extended_column_values.items():
            for val in values:
                value_to_columns.setdefault(val, set()).add(col)

        # 優先順序產生器
        def generate_priority(priority_key: Optional[str]):
            default_priority = [
                ("聲", ["聲", "組", "系"]),
                ("攝", ["攝", "韻"]),
                ("調", ["入", "調"]),
                ("清濁", ["清濁"]),
                ("等", ["等"]),
                ("呼", ["呼"]),
            ]

            if not priority_key:
                return default_priority

            key_order = list(priority_key)
            key_index = {k: i for i, k in enumerate(key_order)}

            ordered = []
            unordered = default_priority.copy()

            # 先把用戶指定的欄位轉為單欄位群組
            for key in key_order:
                ordered.append((key, [key]))

            # 再加入未出現過的 default 群組（只要群組內的欄位不在 priority_key 中）
            for label, cols in default_priority:
                if not any(c in key_order for c in cols):
                    ordered.append((label, cols))

            return ordered

        priority = generate_priority(priority_key)

        while i < len(input_text):
            matched = False
            for j in range(3, 0, -1):
                frag = input_text[i:i + j]

                if frag in {"清", "*清", "@清", "#清"}:
                    pending_clear.append((frag, i, j))
                    i += j
                    matched = True
                    break
                # 特別優先處理清濁的多字值
                if frag in column_values.get("清濁", []) and "清濁" not in used_columns:
                    result.append(f"[{frag}]{{清濁}}")
                    used_columns.add("清濁")
                    match_count += 1
                    i += j
                    matched = True
                    break

                for col in sorted(HIERARCHY_COLUMNS, key=len, reverse=True):  # 長欄位名優先
                    if col == "入":
                        continue
                    if frag.endswith(col) and len(frag) > len(col):
                        val = frag[:-len(col)]
                        # print(f"🧪 嘗試匹配 frag='{frag}' → val='{val}', col='{col}'")
                        if val in column_values.get(col, []):
                            if col not in used_columns:
                                # print(f"✅ 命中：[ {val} ]{{ {col} }}")
                                result.append(f"[{val}]{{{col}}}")
                                used_columns.add(col)
                                match_count += 1
                                i += j
                                matched = True
                                break  # ✅ 跳出 col 的排序迴圈

                if matched:
                    break  # ✅ 跳出 j 的迴圈（for j in 3,2,1）

                if frag not in value_to_columns:
                    continue

                possible_columns = value_to_columns[frag]
                best_group = None
                for group_key, group_members in priority:
                    if any(col in possible_columns for col in group_members):
                        best_group = group_members
                        break

                if not best_group:
                    continue

                matched_in_group = False
                for col in best_group:
                    if col in possible_columns and col not in used_columns:
                        result.append(f"[{frag}]{{{col}}}")
                        used_columns.add(col)
                        match_count += 1
                        i += j
                        matched = True
                        matched_in_group = True
                        break

                if matched_in_group:
                    break

            if not matched:
                return False, 0

        for frag, _, _ in pending_clear:
            options = value_to_columns.get(frag, set())
            voice_used = "聲" in used_columns
            rhyme_used = "韻" in used_columns

            if frag == "*清":
                if "清濁" in options and "清濁" not in used_columns:
                    result.append(f"[清]{{清濁}}")
                    used_columns.add("清濁")
                    match_count += 1
                else:
                    return False, 0
            elif frag == "@清":
                if "聲" in options and "聲" not in used_columns:
                    result.append(f"[清]{{聲}}")
                    used_columns.add("聲")
                    match_count += 1
                else:
                    return False, 0
            elif frag == "#清":
                if "韻" in options and "韻" not in used_columns:
                    result.append(f"[清]{{韻}}")
                    used_columns.add("韻")
                    match_count += 1
                else:
                    return False, 0
            elif frag == "清":
                if "聲" in options and "韻" in options:
                    if not voice_used and not rhyme_used:
                        print("⚠️『清』有歧義（可屬於聲或韻），請使用 @清 或 #清 或 *清 來明確指定。")
                        return False, 0
                    elif voice_used and not rhyme_used:
                        result.append(f"[清]{{韻}}")
                        used_columns.add("韻")
                        match_count += 1
                    elif rhyme_used and not voice_used:
                        result.append(f"[清]{{聲}}")
                        used_columns.add("聲")
                        match_count += 1
                    else:
                        return False, 0
                elif "聲" in options and "聲" not in used_columns:
                    result.append(f"[清]{{聲}}")
                    used_columns.add("聲")
                    match_count += 1
                elif "韻" in options and "韻" not in used_columns:
                    result.append(f"[清]{{韻}}")
                    used_columns.add("韻")
                    match_count += 1
                else:
                    return False, 0

        return "-".join(result), match_count

    if '-' in user_input:
        simplified_to_traditional = {
            "摄": "攝", "呼": "呼", "等": "等", "韵": "韻", "入": "入",
            "调": "調", "清浊": "清濁", "系": "系", "组": "組", "声": "聲",
        }
        prefix, suffix = user_input.split('-', 1)

        fields = []
        temp = suffix
        while temp:
            matched = False
            for field in HIERARCHY_COLUMNS:
                if temp.startswith(field):
                    fields.append(field)
                    temp = temp[len(field):]
                    matched = True
                    break

            if not matched:
                # 嘗試進行簡體轉繁體再匹配
                converted = ""
                i = 0
                while i < len(temp):
                    ch = temp[i]
                    converted += simplified_to_traditional.get(ch, ch)
                    i += 1

                # 再次嘗試用轉換後的字串匹配
                for field in HIERARCHY_COLUMNS:
                    if converted.startswith(field):
                        fields.append(field)
                        temp = temp[len(field):]  # 注意這裡仍用原本的 temp 切除
                        matched = True
                        break

            if not matched:
                print(f"❌ 無效欄位名：「{suffix}」中斷於「{temp}」")
                return False, 0

        # 優先順序：傳入的順序最優先
        priority_key = ''.join(fields)

        # 簡體轉繁體邏輯（保留您的原來邏輯）
        clean_str, _ = s2t_pro(user_input, level=2)
        # print(f"[DEBUG] 原輸入：{user_input} → 繁體轉換後再嘗試：{clean_str}")
        user_input = clean_str

        # 取得每個欄位的合法值
        try:
            value_lists = [column_values[f] for f in fields]
        except KeyError:
            return (False, 0)

        all_results = []
        for combo in product(*value_lists):
            full_input = prefix + ''.join(combo)
            # 使用 generate_priority 動態產生的優先順序
            res = process(full_input, priority_key=priority_key)
            if res[0] is False:
                print(f"⚠️ 略過非法組合：{full_input}")
                continue
            all_results.append(res)

        if not all_results:
            return (False, 0)
        return all_results

    else:
        # ▶ 先試原始輸入（簡體）
        res = process(user_input)
        if res[0] is not False:
            return res

        # ▶ 簡體沒匹配，嘗試繁體
        clean_str, _ = s2t_pro(user_input, level=2)
        # print(f"[DEBUG] 原輸入：{user_input} → 繁體轉換後再嘗試：{clean_str}")
        return process(clean_str)


def auto_convert_batch(input_string: str) -> List[Union[Tuple[str, int], Tuple[bool, int]]]:
    import re
    parts = re.split(r"[,;/，；、]+", input_string.strip())
    results = []
    for idx, part in enumerate(parts):
        if part:
            print(f"🔹 處理第 {idx + 1} 段：{part}")
            res = auto_convert_single(part)
            if isinstance(res, list):
                results.extend(res)
            else:
                results.append(res)
            print(f"   ⮡ 結果: {res}")
    return results


def split_pho_input(input_value: Union[str, List[str]]) -> List[str]:
    """
    將輸入字串或字串列表，依照常見分隔符（空格、逗號、分號、句號）拆分為項目列表。

    參數：
        input_value: str 或 List[str]

    回傳：
        List[str]
    """
    # 支援的分隔符：空格、, 、； 、. 、tab、中文頓號、全形逗號
    delimiters = r"[ ,;.;、，；\t]+"

    # 確保轉為列表統一處理
    if isinstance(input_value, str):
        input_value = [input_value]

    result = []
    for item in input_value:
        item = item.strip()
        if item:
            parts = re.split(delimiters, item)
            parts = [p for p in parts if p]  # 過濾空字串
            result.extend(parts)

    return result


def query_dialect_abbreviations(
        region_input=None,
        location_sequence=None,
        db_path=QUERY_DB_PATH,
        tables="dialects",
        need_storage_flag=True,  # 新增參數
        debug=False
):
    """
    查詢 dialects 表的簡稱欄位，支持完全匹配和元素模糊匹配。

    參數：
    - region_input: 字串或列表。可為完整音典分區字串（如 '華北-河北-東北'）或單個元素（如 '河北'）或元素列表
    - location_sequence: 地點字串，如 '河北/歷史音；東北'
    - debug: 是否輸出調試資訊

    返回：
    - 簡稱列表（排序去重）
    """

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"資料庫不存在: {db_path}")

    if debug:
        print("=== 查詢開始 ===")
        print(f"region_input: {region_input}")
        print(f"location_sequence: {location_sequence}")

    # 處理 region_input 為列表
    if isinstance(region_input, str):
        region_list = [region_input.strip()]
    elif isinstance(region_input, list):
        region_list = [r.strip() for r in region_input if isinstance(r, str)]
    else:
        region_list = []

    if isinstance(location_sequence, str):
        location_list = [location_sequence.strip()]
    elif isinstance(location_sequence, list):
        location_list = [item.strip() for item in location_sequence if isinstance(item, str)]
    else:
        location_list = []

    combined_elements = list(set(region_list))

    if debug:
        print(f"分區合併後元素: {combined_elements}")

    result = []
    seen = set()

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        query = f"""
            SELECT 音典分區, 簡稱 
            FROM {tables} 
            WHERE 1=1
        """
        if need_storage_flag:
            query += " AND 存儲標記 IS NOT NULL AND 存儲標記 != ''"
        cursor.execute(query)
        all_rows = cursor.fetchall()

        for item in region_list:
            found_exact = False
            for partition_str, abbr in all_rows:
                if item == partition_str:
                    if abbr not in seen:
                        result.append(abbr)
                        seen.add(abbr)
                    found_exact = True
            if not found_exact:
                for partition_str, abbr in all_rows:
                    if item in partition_str.split("-"):
                        if abbr not in seen:
                            result.append(abbr)
                            seen.add(abbr)

    # 最終結果：保留匹配順序，直接拼接原始地點
    final_result = result + location_list

    if debug:
        print(f"=== 最終結果（保留資料庫順序 + 地點）: {final_result} ===")

    return final_result


def get_coordinates_from_db(abbreviation_list, supplementary_abbreviation_list=None,
                            db_path=QUERY_DB_PATH, use_supplementary_db=False):
    print("即將處理經緯度")

    # Haversine 公式計算兩點間的距離，單位為公里
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # 地球半徑，單位為公里
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c  # 返回距離，單位為公里
        return distance

    def get_optimal_zoom(lat_diff, lon_diff):
        # 使用經度和緯度差來計算最大距離
        max_diff = max(lat_diff, lon_diff)

        # 除以6得到單位距離（距離/6）
        unit_distance = 1000 * max_diff / 6

        # 根據距離尋找合適的zoom層級
        zoom_to_distance = {
            20: 10, 19: 10, 18: 25, 17: 50, 16: 100,
            15: 200, 14: 500, 13: 1000, 12: 2000, 11: 5000,
            10: 10000, 9: 20000, 8: 30000, 7: 50000, 6: 100000,
            5: 200000, 4: 500000, 3: 1000000, 2: 2000000
        }

        # 從字典中找到合適的zoom層級
        for zoom, distance_threshold in zoom_to_distance.items():
            if unit_distance <= distance_threshold:
                return zoom
        # 如果沒有找到合適的值（通常不會發生）
        return 10

    if supplementary_abbreviation_list:
        # 刪除 supplementary_abbreviation_list 中已經在 abbreviation_list 中的元素
        supplementary_abbreviation_list = [abbr for abbr in supplementary_abbreviation_list if
                                           abbr not in abbreviation_list]
    abbreviation_list = [abbreviation for abbreviation in abbreviation_list if abbreviation]

    # 連接到查詢數據庫
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 用於存儲結果的列表
    result = []
    latitudes = []
    longitudes = []
    abbreviation_lat_lon_pairs = []  # 用來存儲簡稱和經緯度的配對

    # 根據簡稱查詢經緯度（主數據庫）
    for abbreviation in abbreviation_list:
        # 執行SQL查詢，選取簡稱匹配的行並獲取經緯度
        cursor.execute("SELECT 經緯度 FROM dialects WHERE 簡稱=?", (abbreviation,))
        row = cursor.fetchone()

        # 如果找到了匹配的行，處理經緯度
        if row:
            lat_lon_str = row[0]
            try:
                # 解析經緯度字符串，將其轉換為浮點數元組
                # latitude, longitude = map(float, re.split(r'[,，\s;]+', lat_lon_str))
                if lat_lon_str:
                    latitude, longitude = map(float, re.split(r'[,，\s;]+', lat_lon_str))
                    # print(latitude, longitude)
                else:
                    # 处理 lat_lon_str 为 None 或空字符串的情况
                    print("错误：lat_lon_str 为空或为 None！")
                    # 你可以根据需要返回默认值，或者抛出异常
                    latitude, longitude = None, None
                result.append((latitude, longitude))
                latitudes.append(latitude)
                longitudes.append(longitude)
                abbreviation_lat_lon_pairs.append((abbreviation, (latitude, longitude)))  # 存儲簡稱與經緯度配對
            except ValueError:
                print(f"無法解析經緯度：{lat_lon_str}")
        else:
            print(f"未找到簡稱：{abbreviation}")

    # 如果需要，從補充數據庫中讀取數據
    if use_supplementary_db and supplementary_abbreviation_list:
        # 連接到補充數據庫
        conn_supplementary = sqlite3.connect(SUPPLE_DB_PATH)
        cursor_supplementary = conn_supplementary.cursor()

        # 使用補充的簡稱列表進行查詢
        for abbreviation in supplementary_abbreviation_list:
            # 執行SQL查詢，選取簡稱匹配的行並獲取經緯度
            cursor_supplementary.execute("SELECT 經緯度 FROM informations WHERE 簡稱=?", (abbreviation,))
            row = cursor_supplementary.fetchone()

            # 如果找到了匹配的行，處理經緯度
            if row:
                lat_lon_str = row[0]
                try:
                    # 解析經緯度字符串，將其轉換為浮點數元組
                    latitude, longitude = map(float, re.split(r'[，,]', lat_lon_str))
                    result.append((latitude, longitude))
                    latitudes.append(latitude)
                    longitudes.append(longitude)
                    abbreviation_lat_lon_pairs.append((abbreviation, (latitude, longitude)))  # 存儲簡稱與經緯度配對
                except ValueError:
                    print(f"無法解析經緯度：{lat_lon_str}")
            else:
                print(f"未找到簡稱：{abbreviation}")

        conn_supplementary.close()

    valid_latitudes = [lat for lat in latitudes if lat is not None]
    valid_longitudes = [lon for lon in longitudes if lon is not None]

    if valid_latitudes and valid_longitudes:
        # 计算中心经纬度
        center_latitude = (max(valid_latitudes) + min(valid_latitudes)) / 2
        center_longitude = (max(valid_longitudes) + min(valid_longitudes)) / 2

        # 保留6位小数
        center_coordinate = [round(center_latitude, 6), round(center_longitude, 6)]

        # 计算横向最大距离（经度差）
        max_lon_distance = 0
        max_lat_distance = 0

        # 计算最大经度距离（横向）
        for i in range(len(valid_longitudes)):
            for j in range(i + 1, len(valid_longitudes)):
                max_lon_distance = max(max_lon_distance,
                                       haversine(valid_latitudes[i], valid_longitudes[i], valid_latitudes[j],
                                                 valid_longitudes[i]))

        # 计算最大纬度距离（纵向）
        for i in range(len(valid_latitudes)):
            for j in range(i + 1, len(valid_latitudes)):
                max_lat_distance = max(max_lat_distance,
                                       haversine(valid_latitudes[i], valid_longitudes[i], valid_latitudes[i],
                                                 valid_longitudes[j]))

        # 保留2位小数
        max_lat_distance = round(max_lat_distance, 2)
        max_lon_distance = round(max_lon_distance, 2)

        # 根据最大距离计算合适的 zoom 层级
        zoom_level = get_optimal_zoom(max_lat_distance, max_lon_distance)
    else:
        center_coordinate = None
        max_lat_distance = max_lon_distance = 0
        zoom_level = None

    # 關閉數據庫連接
    conn.close()

    # 返回結果，包括經緯度與簡稱配對、中心經緯度、最大縱向和橫向距離，以及對應的zoom層級
    coordinates = {
        "coordinates_locations": abbreviation_lat_lon_pairs,  # 返回簡稱與經緯度的配對
        "center_coordinate": center_coordinate,
        "max_distances": {
            "lat_km": max_lat_distance,
            "lon_km": max_lon_distance,
        },
        "zoom_level": zoom_level  # 返回選擇的zoom層級
    }

    return coordinates


def read_partition_hierarchy(parent_regions=None, db_path=QUERY_DB_PATH):
    """
    傳入 parent_region，返回它下層的分區：
    - 一級 → 回傳其二級列表
    - 二級 → 回傳其三級列表（僅該一級下）
    - 其他 → []
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"資料庫不存在: {db_path}")

    hierarchy = defaultdict(lambda: defaultdict(list))

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 音典分區 FROM dialects")
        rows = cursor.fetchall()

        for (partition_str,) in rows:
            parts = partition_str.strip().split("-")
            if len(parts) == 1:
                if parts[0] not in hierarchy:
                    hierarchy[parts[0]] = {}
            elif len(parts) == 2:
                if parts[1] not in hierarchy[parts[0]]:
                    hierarchy[parts[0]][parts[1]] = []
            elif len(parts) >= 3:
                if parts[2] not in hierarchy[parts[0]][parts[1]]:
                    hierarchy[parts[0]][parts[1]].append(parts[2])

    # print("完整的 hierarchy 結構:")
    # import json
    # print(json.dumps(hierarchy, ensure_ascii=False, indent=4))
    # 處理 parent_regions 輸入
    if isinstance(parent_regions, str):
        parent_regions = [parent_regions]
    elif not parent_regions:
        return dict(hierarchy)  # 無輸入時返回整體結構

    # 對每個 parent_region 查詢其下層及層級
    result = {}
    for region in parent_regions:
        print(f"處理區域: {region}")  # 顯示當前處理的區域

        if region in hierarchy:
            # print(f"找到一級分區: {region}")
            result[region] = sorted(hierarchy[region].keys())
            level = 1  # 一級的層級為 1
            # print(f"一級分區的下層分區: {sorted(hierarchy[region].keys())}, 層級: {level}")
        else:
            found = False
            # print(f"在一級分區中未找到: {region}，開始查找二級分區")

            for level1, level2_dict in hierarchy.items():
                # print(f"檢查一級分區 {level1} 下的二級分區")
                if region in level2_dict:
                    # print(f"找到二級分區: {region} 在 {level1} 下")
                    result[region] = sorted(hierarchy[level1][region])
                    level = 2  # 二級的層級為 2
                    # print(f"二級分區的下層分區: {sorted(hierarchy[level1][region])}, 層級: {level}")
                    found = True
                    break

            if not found:
                # print(f"未找到二級分區 {region}，開始查找三級分區")
                result[region] = []

                # 確保三級分區返回空列表並設置層級為 3
                for level1, level2_dict in hierarchy.items():
                    # print(f"檢查一級分區 {level1} 下的二級分區")
                    for level2, level3_list in level2_dict.items():
                        if isinstance(level3_list, list):  # 確保該二級分區擁有三級分區
                            if region in level3_list:
                                # print(f"找到三級分區: {region} 在 {level1}-{level2} 下，設置層級為 3")
                                result[region] = []  # 返回空列表
                                level = 3  # 設置層級為 3
                                found = True
                                break
                    if found:
                        break

                if not found:
                    level = 0  # 無法匹配，層級為 0
                    # print(f"未找到三級分區 {region}，層級設置為 0")

        # print(f"最終結果: {region} -> {result[region]}")

        # 保留原來的結構，並加上 level
        result[region] = {"partitions": result[region], "level": level}

    return result


# results = auto_convert_single("宕")
# locations = [""]
# regions = ["嶺南","閩西"]
# abbreviations_list = query_dialect_abbreviations(regions,locations)
# # print(abbreviations_list)
# result = get_coordinates_from_db(abbreviations_list)
# # # # results = match_locations_batch("東莞")
# print(results)
# print(results[1])
# print(results[2])
# print(results[3])
# print(results[4])
# print(results[5])
# print(results[6])
# print(results[7])
