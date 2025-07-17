import re
import sqlite3
from pypinyin import lazy_pinyin
import Levenshtein

from format_convert import s2t_pro
from typing import Tuple, Union, List

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

# 優先邏輯（分層關係）
priority = [
    ("聲", ["聲", "組", "系"]),
    ("攝", ["攝", "韻"]),
    ("調", ["入", "調"]),
    ("清濁", ["清濁"]),
    ("等", ["等"]),
    ("呼", ["呼"]),
]


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

    converted, _ = s2t_pro(user_input, level=2)
    possible_inputs = {user_input, converted}

    conn = sqlite3.connect(QUERY_DB_PATH)
    cursor = conn.cursor()

    matched_abbrs = set()
    for term in possible_inputs:
        cursor.execute("SELECT 簡稱 FROM dialects WHERE 簡稱 = ?", (term,))
        exact = cursor.fetchall()
        matched_abbrs.update([row[0] for row in exact])
        print(f"[DEBUG] 完全匹配【{term}】：{exact}")

    if matched_abbrs:
        return list(matched_abbrs), 1, [], [], [], [], [], []

    fuzzy_abbrs = set()
    for term in possible_inputs:
        cursor.execute("SELECT 簡稱 FROM dialects WHERE 簡稱 LIKE ?", (term + "%",))
        fuzzy = cursor.fetchall()
        fuzzy_abbrs.update([row[0] for row in fuzzy])
        print(f"[DEBUG] 模糊簡稱匹配【{term}】：{fuzzy}")

    geo_matches = set()
    geo_abbr_map = {}
    all_geo_names = []
    all_abbr_names = []

    for col in ["鎮", "行政村", "自然村"]:
        cursor.execute(f"SELECT {col}, 簡稱 FROM dialects")
        rows = cursor.fetchall()
        for name, abbr in rows:
            all_geo_names.append(name)
            all_abbr_names.append(abbr)
            for term in possible_inputs:
                if term in (name or ""):
                    geo_matches.add(name)
                    geo_abbr_map[name] = abbr

    # 收集全部簡稱，準備做相似與音近比對
    cursor.execute("SELECT 簡稱 FROM dialects")
    all_abbrs = [row[0] for row in cursor.fetchall()]

    fuzzy_geo_matches = set()
    fuzzy_geo_abbrs = set()
    sound_like_matches = set()
    sound_like_abbrs = set()

    for name, abbr in zip(all_geo_names + all_abbrs, all_abbr_names + all_abbrs):
        if not name or not abbr:
            continue  # 跳過空值

        # Levenshtein 相似比對
        if is_similar(user_input, name):
            print(f"[DEBUG] 相似匹配: '{user_input}' ≈ '{name}' (abbr: {abbr})")
            fuzzy_geo_matches.add(name)
            fuzzy_geo_abbrs.add(abbr)

        # 拼音比對
        if is_pinyin_similar(user_input, name):
            print(f"[DEBUG] 拼音匹配: '{user_input}' ≈ '{name}' (abbr: {abbr})")
            sound_like_matches.add(name)
            sound_like_abbrs.add(abbr)

    return (
        list(fuzzy_abbrs),  # 簡稱完全或前綴匹配結果
        0,  # 是否完全匹配
        list(geo_matches),  # 鎮/行政村/自然村 中的模糊匹配
        [geo_abbr_map[n] for n in geo_matches],  # 地名對應的簡稱
        list(fuzzy_geo_matches),  # Levenshtein 相似匹配（簡稱 + 地名）
        list(fuzzy_geo_abbrs),
        list(sound_like_matches),  # 拼音相近匹配（簡稱 + 地名）
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
    def process(input_text: str) -> Union[Tuple[str, int], Tuple[bool, int]]:
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
        # print("22222")

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
                        if val in column_values.get(col, []):  # 確保是合法值
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

            # ✅ 這是新加的，for j 結束後還是沒匹配，就 return
            if not matched:
                return False, 0

        # print("11111")

        # 延遲處理所有清類型
        for frag, _, _ in pending_clear:
            options = value_to_columns.get(frag, set())
            voice_used = "聲" in used_columns
            rhyme_used = "韻" in used_columns

            # print(f"\n🔸 延遲處理『{frag}』：可配欄位 {options}，已使用 {used_columns}")

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
            print(f"   ⮡ 結果: {res}")
            results.append(res)
    return results


# results = match_locations_batch("动坑")
# print(results)
# print(results[1])
# print(results[2])
# print(results[3])
# print(results[4])
# print(results[5])
# print(results[6])
# print(results[7])
