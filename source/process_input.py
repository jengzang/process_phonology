import os
import re
import sqlite3
from collections import defaultdict
from itertools import product

from pypinyin import lazy_pinyin
import Levenshtein

from source.format_convert import s2t_pro
from typing import Tuple, Union, List, Optional

from source.config import QUERY_DB_PATH

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


def match_locations(user_input):
    def is_pinyin_similar(a, b):
        if not a or not b:
            return False
        return lazy_pinyin(a) == lazy_pinyin(b)

    def is_similar(a, b, threshold=0.7):
        if not a or not b:
            return False
        max_len = max(len(a), len(b))
        return 1 - Levenshtein.distance(a, b) / max_len >= threshold

    print(f"[DEBUG] 使用者輸入：{user_input}")

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

    # 撈出所有存儲標記 = 1 的合法簡稱
    cursor.execute("SELECT 簡稱 FROM dialects WHERE 存儲標記 = 1")
    valid_abbrs_set = set(row[0] for row in cursor.fetchall())

    matched_abbrs = set()
    for term in possible_inputs:
        cursor.execute("SELECT 簡稱 FROM dialects WHERE 簡稱 = ? AND 存儲標記 = 1", (term,))
        exact = cursor.fetchall()
        matched_abbrs.update([row[0] for row in exact])
        print(f"[DEBUG] 完全匹配【{term}】：{exact}")

    if matched_abbrs:
        return list(matched_abbrs), 1, [], [], [], [], [], []

    fuzzy_abbrs = set()
    for term in possible_inputs:
        cursor.execute("SELECT 簡稱 FROM dialects WHERE 簡稱 LIKE ? AND 存儲標記 = 1", (term + "%",))
        fuzzy = cursor.fetchall()
        fuzzy_abbrs.update([row[0] for row in fuzzy])
        print(f"[DEBUG] 模糊簡稱匹配【{term}】：{fuzzy}")

    geo_matches = set()
    geo_abbr_map = {}
    all_geo_names = []
    all_abbr_names = []

    for col in ["鎮", "行政村", "自然村"]:
        cursor.execute(f"SELECT {col}, 簡稱 FROM dialects WHERE 存儲標記 = 1")
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
            print(f"[DEBUG] 相似匹配: '{user_input}' ≈ '{name}' (abbr: {abbr})")
            fuzzy_geo_matches.add(name)
            fuzzy_geo_abbrs.add(abbr)

        if is_pinyin_similar(user_input, name):
            print(f"[DEBUG] 拼音匹配: '{user_input}' ≈ '{name}' (abbr: {abbr})")
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


def match_locations_batch(input_string: str):
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
            print(f"\n🔹 處理第 {idx + 1} 個地名：{part}")
            try:
                res = match_locations(part)
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

                for col in HIERARCHY_COLUMNS:
                    if col == "入":
                        continue
                    if frag.endswith(col) and len(frag) > len(col):
                        val = frag[:-len(col)]
                        if val in column_values.get(col, []):
                            if col not in used_columns:
                                result.append(f"[{val}]{{{col}}}")
                                used_columns.add(col)
                                match_count += 1
                                i += j
                                matched = True
                                break

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
                print(f"❌ 無效欄位名：「{suffix}」中斷於「{temp}」")
                return (False, 0)

        # 優先順序：傳入的順序最優先
        priority_key = ''.join(fields)

        # 簡體轉繁體邏輯（保留您的原來邏輯）
        clean_str, _ = s2t_pro(user_input, level=2)
        print(f"[DEBUG] 原輸入：{user_input} → 繁體轉換後再嘗試：{clean_str}")
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
        print(f"[DEBUG] 原輸入：{user_input} → 繁體轉換後再嘗試：{clean_str}")
        return process(clean_str)




def auto_convert_batch(input_string: str) -> List[Union[Tuple[str, int], Tuple[bool, int]]]:
    import re
    parts = re.split(r"[ ,;/，；、]+", input_string.strip())
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
        print(f"合併後元素: {combined_elements}")

    result = []
    seen = set()

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 音典分區, 簡稱 
            FROM dialects 
            WHERE 存儲標記 IS NOT NULL AND 存儲標記 != ''
        """)
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

    # 處理 parent_regions 輸入
    if isinstance(parent_regions, str):
        parent_regions = [parent_regions]
    elif not parent_regions:
        return dict(hierarchy)  # 無輸入時返回整體結構

    # 對每個 parent_region 查詢其下層
    result = {}
    for region in parent_regions:
        if region in hierarchy:
            result[region] = sorted(hierarchy[region].keys())
        else:
            found = False
            for level1, level2_dict in hierarchy.items():
                if region in level2_dict:
                    result[region] = sorted(hierarchy[level1][region])
                    found = True
                    break
            if not found:
                result[region] = []

    return result

results = auto_convert_single("通开一")
# # # results = match_locations_batch("東莞")
print(results)
# print(results[1])
# print(results[2])
# print(results[3])
# print(results[4])
# print(results[5])
# print(results[6])
# print(results[7])
