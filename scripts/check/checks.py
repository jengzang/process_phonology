"""
📘【可使用的指令格式與說明】👇

每次輸入指令後，按 Enter 執行。可一次輸入多條指令，用英文分號 ; 分隔。
若直接按 Enter，則進入聲調處理邏輯。

============================
🛠 指令類型與格式：
============================

1️⃣ 漢字欄替換/刪除（以某漢字定位）

  c-漢字-新字         ➤ 將“漢字”替換為“新字”
  c-漢字-d            ➤ 清空該行（整行設為空）

  ✅ 範例：
    c-帥-好            將“帥”字改為“好”
    c-帥-d             清空包含“帥”的那一整行
    c-帥-d-123         清空“帥”所在第 123 行（多音字時需要指定）

2️⃣ 音標欄替換（以某漢字定位）

  i-漢字-新音標      ➤ 將“漢字”所在行的音標欄改為“新音標”

  ✅ 範例：
    i-帥-jat4          把“帥”的音標改為 jat4
    i-帥-jat4-123      如果“帥”出現多次，用這個方式指定第 123 行

3️⃣ 音標欄全局替換（無需指定漢字）

  p-原字元-新字元     ➤ 將音標欄中的所有“原字元”替換為“新字元”

  ✅ 範例：
    p-'-ʰ              把所有音標中的 ' 替換為 ʰ

4️⃣ 聲調替換（依據尾音是否為入聲/舒聲）

  r原>新             ➤ 替換入聲調值（例：r031>3 表示把入聲的 031 改為 3）
  s原>新             ➤ 替換舒聲調值（例：s25>55 表示把舒聲的 25 改為 55）

  ✅ 範例：
    r021>21           將入聲的 021 改為 21（0 開頭視為同一組）
    s33>55            將舒聲的 33 改為 55

5️⃣ 處理並替換零聲母

    行號 替換格式（原>新）

    ✅ 範例：
      0 y>i           ➤ 第 0 行中將 y 改為 i
      1~3 u>wu         ➤ 第 1 到 3 行的資料將 u 改為 wu

6️⃣ 查詢聲母或韻母後進行修改（查詢介面）

    🔍 可輸入「聲母 / 韻母」查詢（可多個）
    例如：j i u         ➤ 查找聲母為 j，或韻母為 i、u 的資料

    查詢後使用指令：
      行號 替換指令    ➤ 例如：0~2 i>y

  ✅ 多筆指令可用分號 ; 一次輸入：
    p-'-ʰ; r031>3; i-帥-jat4-1355; c-帥-d-1234


============================
⚠️ 特別注意：
============================

- c/i 類指令若定位漢字重複（多音字），請加上「-行號」避免模糊。
- 每次替換後，系統會自動顯示所有聲調分佈與資料格式檢查結果。
- 多條指令用英文分號 ; 分隔。例如：
    p-'-ʰ; r031>3; i-帥-jat4-1355; c-帥-d-1234

============================
📊 格式檢查說明：
============================

1️⃣ 非單字漢字：檢查漢字欄是否為單個字元
2️⃣ 缺聲調：音標欄若無正常數字或上標數字結尾，會列為缺聲調
3️⃣ 音標異常：若音標欄中含有 , . ; ' / - = 等符號，且前後不為有效音節 → 顯示異常

✅ 若所有資料皆正常，會顯示「格式檢查通過，無異常」

"""
import os
import re
import sys
import tkinter as tk
from collections import defaultdict
from tkinter import filedialog

import pandas as pd

from source.format_convert import process_縣志_word, process_跳跳老鼠, process_縣志_excel, process_音典

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # 添加项目根目录到 sys.path
from maybe_error_chars import check_get_chars
from source.get_new import extract_all_from_files

RU_FINALS = set("ptkʔˀᵖᵏᵗbdg")
SUPER_TO_NORMAL = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")


def 處理自定義編輯指令(df, col_hanzi, col_ipa, command):
    results = []
    errors = []

    commands = [cmd.strip() for cmd in command.split(";") if cmd.strip()]
    for cmd in commands:
        if not cmd:
            continue
        parts = cmd.split("-")

        if len(parts) < 3:
            errors.append(f"❌ 無效指令格式：{cmd}")
            continue

        action = parts[0]
        key = parts[1]
        value = parts[2]
        row_id = int(parts[3]) if len(parts) == 4 and parts[3].isdigit() else None

        # ✅ 處理「全表音標替換」指令：p-原字元-新字元
        if action == "p":
            df[col_ipa] = df[col_ipa].astype(str).str.replace(key, value, regex=False)
            results.append(f"✅ 全表音標替換：{key} → {value}")
            continue

        # ✅ 其他指令（需定位漢字）
        matches = df[df[col_hanzi] == key]
        if len(matches) == 0:
            errors.append(f"❌ 找不到漢字：{key}")
            continue
        elif len(matches) > 1 and not row_id:
            ids = matches.index.tolist()
            suggestion = "; ".join([f"{idx} {key}" for idx in ids])
            errors.append(
                f"⚠️ 找到多個“{key}” → 請使用行號區分：\n"
                + f"→ 建議指令：{cmd}-{ids[0]} 或 {cmd}-{ids[1]} 等\n"
                + suggestion
            )
            continue

        # 🔍 確定目標行
        target_row = row_id if row_id is not None else matches.index[0]

        if action == "c":
            if value == "d":
                df.loc[target_row] = ""
                results.append(f"✅ 已清空行 {target_row}（漢字：{key}）")
            else:
                df.at[target_row, col_hanzi] = value
                results.append(f"✅ 替換漢字：{key} → {value}（行 {target_row}）")

        elif action == "i":
            df.at[target_row, col_ipa] = value
            results.append(f"✅ 修改音標：{key} → {value}（行 {target_row}）")

        else:
            errors.append(f"❌ 不支援的指令類型：{action}")

    return results, errors


def 檢查資料格式(df, col_hanzi, col_ipa, display=False, col_note=None):
    def is_single_chinese(char):
        return len(char) == 1 and '\u4e00' <= char <= '\u9fff'

    def is_normal_ipa(s):
        allowed = set(
            "abcdefghijklmnopqrstuvwxyz"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "ŋɑɐɒɓʙβɔɕçðɖɗɘəɚɛɜɞɟʄɡɢʛɣʰɥʜɦɪʝɭɬɫʟɮɰɱɲȵɳŋɳɴɵøœæɶɸɹɻʁʀɽɾʃʂʈʊʋʌʍχʎʑʐʒʔʕʡʢʘʞθʼˈˌːˑ⁰¹²³⁴⁵⁶⁷⁸⁹ⁿˡʲʳˀ"
            "ʦʧʨʂʐʑʒʮʰʲː˞ˠˤ~^̃"
            "ıſɩɷʅɥʯεɝɚᴇãẽĩỹõúαɤᵘᶷᶤᶶᵚʸᶦᵊⁱ◌∅ɯʦʒɿ̍ʷ̯̩"
            "0123456789"
        )
        return all(c in allowed for c in s)

    errors = {
        "非單字漢字": [],
        "異常音標": [],
        "缺聲調": []
    }
    # print(df)
    for i, row in df.iterrows():
        hanzi = str(row.get(col_hanzi, "")).strip()
        ipa = str(row.get(col_ipa, "")).strip()

        if not hanzi or not ipa:
            continue  # 跳過空行或空漢字/音標

        if not is_single_chinese(hanzi):
            errors["非單字漢字"].append((i, hanzi))

        match = re.search(r"[0-9¹²³⁴⁵⁶⁷⁸⁹⁰]{1,4}$", ipa)
        if not match:
            errors["缺聲調"].append((i, hanzi))
            continue

        if any(sep in ipa for sep in ",;/\\"):
            # 如果包含分隔符，拆分成多个部分
            parts = re.split(r"[,;/\\]", ipa)
        else:
            # 如果没有分隔符，直接将 ipa 字符串作为一个整体检查
            parts = [ipa]
        if ipa.isdigit():
            errors["異常音標"].append((i, hanzi, ipa))
            continue
        if not all(is_normal_ipa(p.strip()) for p in parts if p.strip()):
            errors["異常音標"].append((i, hanzi, ipa))

    # 錯誤輸出
    for k, v in errors.items():
        if v:
            print(f"\n⚠️ [{k}] 發現 {len(v)} 項：")
            count = 0  # 用於控制每行最多顯示4個錯誤
            for item in v:
                if count == 4:  # 每4个错误换行
                    print()  # 换行
                    count = 0  # 重置计数器
                print(item, end="   ")  # 不换行，条目之间加空格
                count += 1

    if not any(errors.values()):
        print("✅ 格式檢查通過，無異常")

    # 額外：顯示每一行內容（可選）
    if display:
        print("\n🧾 所有資料（行號｜漢字｜音標｜註釋）：")
        for i, row in df.iterrows():
            hanzi = str(row.get(col_hanzi, "")).strip()
            ipa = str(row.get(col_ipa, "")).strip()
            note = str(row.get(col_note, "")).strip() if col_note and col_note in row else ""

            # 跳過漢字與音標都為空的行
            if not hanzi and not ipa:
                continue

            print(f"[{i}] {hanzi}｜{ipa}｜{note}")


def 整理並顯示調值(df_xlsx, actual_cols):
    ru_rawtone_to_hanzi = defaultdict(set)
    shu_tone_to_hanzi = defaultdict(set)

    for _, row in df_xlsx.iterrows():
        ipa = row[actual_cols['音標']]
        hanzi = row[actual_cols['漢字']]
        match = re.search(r"([0-9¹²³⁴⁵⁶⁷⁸⁹⁰]{1,4})$", str(ipa))
        if not match:
            continue

        tone_raw = match.group(1)
        tone = tone_raw.translate(SUPER_TO_NORMAL)
        head = ipa[:-len(tone_raw)]
        prev_char = head[-1] if head else ""
        ends_with_ru = prev_char in RU_FINALS

        if ends_with_ru:
            ru_rawtone_to_hanzi[tone].add(hanzi)
        else:
            shu_tone_to_hanzi[tone].add(hanzi)

    # 入聲調值顯示（合併原調值）
    merged_ru = defaultdict(lambda: {"raw_tones": set(), "hanzi": set()})
    for t, chars in ru_rawtone_to_hanzi.items():
        key = t.lstrip("0")
        merged_ru[key]["raw_tones"].add(t)
        merged_ru[key]["hanzi"].update(chars)

    print("▶ 入聲調值：")
    for key in sorted(merged_ru.keys(), key=lambda x: int(x)):
        label = "/".join(sorted(merged_ru[key]["raw_tones"], key=lambda x: int(x)))
        hanzi_str = "".join(sorted(merged_ru[key]["hanzi"]))
        print(f"{label}: {hanzi_str}")

    print("\n▶ 舒聲調值：")
    for t in sorted(shu_tone_to_hanzi.keys(), key=lambda x: int(x)):
        print(f"{t}: {''.join(sorted(shu_tone_to_hanzi[t]))}")


def 處理批次編輯指令(df_xlsx, filtered_df, actual_cols, edit_input):
    results = []
    errors = []

    # 支援格式如 "0 y>i;1~3 o>i"
    commands = [cmd.strip() for cmd in edit_input.split(";") if cmd.strip()]

    for cmd in commands:
        # 拆分範圍與替換指令
        try:
            range_part, replace_part = cmd.split()
        except ValueError:
            errors.append(f"❌ 格式錯誤，缺少空格分隔：{cmd}")
            continue

        # 解析替換內容：例如 "y>i"
        if ">" not in replace_part:
            errors.append(f"❌ 替換格式錯誤（需使用 >）：{cmd}")
            continue
        old, new = replace_part.split(">", 1)

        # 解析行號範圍
        if "~" in range_part:
            try:
                start, end = map(int, range_part.split("~"))
                indices = list(range(start, end + 1))
            except:
                errors.append(f"❌ 行號範圍格式錯誤：{range_part}")
                continue
        else:
            try:
                indices = [int(range_part)]
            except:
                errors.append(f"❌ 行號格式錯誤：{range_part}")
                continue

        # 逐行處理
        for i in indices:
            if i < 0 or i >= len(filtered_df):
                errors.append(f"❌ 行號 {i} 超出範圍")
                continue

            # 取得原始行號，對應回 df_xlsx
            original_index = filtered_df.iloc[i]["原始行號"]

            if original_index not in df_xlsx.index:
                errors.append(f"❌ 找不到原始行 {original_index}（對應於排序後第 {i} 行）")
                continue

            row_result = f"📝 第 {i} 行（原始行 {original_index}）："

            # 處理每個目標欄位（目前僅漢字與音標）
            for label, colname in actual_cols.items():
                old_value = df_xlsx.at[original_index, colname]
                new_value = old_value.replace(old, new, 1)
                if new_value != old_value:
                    df_xlsx.at[original_index, colname] = new_value
                    row_result += f"【{label}】{old_value} → {new_value}；"

            if "；" in row_result:
                results.append(row_result)
            else:
                results.append(f"📎 第 {i} 行未發現可替換內容（原始行 {original_index}）")

    return results, errors


def 查找出韻字(df_xlsx, actual_cols, chars_list):
    num = len(chars_list)
    # 查找并输出指定的漢字的讀音
    print(f"\n📝 以下字可能有誤(出韻),共有{num}個：")
    count = 0
    for i, row in df_xlsx.iterrows():
        hanzi = str(row.get(actual_cols['漢字'], "")).strip()
        ipa = str(row.get(actual_cols['音標'], "")).strip()
        note = str(row.get(actual_cols['解釋'], "")).strip()

        # 只查找在指定列表中的漢字
        if hanzi in chars_list:
            if count == 4:  # 每4个条目换行
                print()  # 换行
                count = 0  # 重置计数器
            print(f"[{i}] {hanzi}｜{ipa}｜{note}", end=" \t\t ")  # 不换行
            count += 1


# 排序規則定義
custom_order = [
    'p', 'pʰ', 't', 'tʰ', 'k', 'kʰ', 'f', 'ʋ', 'ɸ', 'h',
    'x', 'l', 'n', 'm', 'ŋ', 'ɲ', 'ȵ', 'j', 'z', 's', 'ʃ',
    'ʂ', 'ɕ', 'θ', 'ɬ', 'b', 'd', 'g', 'ʒ', 'ʑ', 'ʐ',
    'ʦ', 'ʧ', 'ʨ', 'tʂ', 'tɹ', 'tr', 'tθ', 'dz', 'dʑ', 'dʐ', 'dʒ',
    'ʦʰ', 'ʧʰ', 'ʨʰ', 'tʂʰ', 'tɹʰ', 'trʰ', 'tθʰ', 'dzʰ', 'dʑʰ', 'dʐʰ', 'dʒʰ',
    'ʔ', 'a', 'ia', 'ua', 'ᴀ', 'ɑ', 'æ', 'ɐ', 'iɐ', 'uɐ',
    'ə', 'iə', 'uə', 'ᴇ', 'ɛ', 'œ', 'iɛ', 'uɛ', 'ɜ', 'ɞ', 'ʌ',
    'ɔ', 'iɔ', 'uɔ', 'o', 'io', 'uo', 'ɤ', 'ɵ', 'ɘ',
    'ø', 'iø', 'e', 'ie', 'ʊ', 'u', 'ɯ', 'y', 'i', 'ɿ', 'ʮ'
]


def sort_by_custom_order(series):
    counts = series.dropna().astype(str)
    counts = counts[counts != ""]
    value_counts = counts.value_counts()

    def custom_key(token):
        for length in range(3, 0, -1):  # 優先取3/2個字元當 key
            sub = token[:length]
            if sub in custom_order:
                return custom_order.index(sub)
        return float('inf')

    sorted_series = value_counts.sort_index(key=lambda idx: [custom_key(i) for i in idx])
    return sorted_series


def print_counts_in_rows(counts, per_row=5):
    # 將 key:value 轉為字串並對齊格式
    max_key_len = max(len(str(k)) for k in counts.index)
    max_val_len = max(len(str(v)) for v in counts.values)

    items = [f"{k:<{max_key_len}}:{v:>{max_val_len}}" for k, v in counts.items()]

    for i in range(0, len(items), per_row):
        print("    ".join(items[i:i + per_row]))


priority_order = ['u', 'i', 'y', 'm', 'p', 'n', 't', 'ŋ', 'k', 'ʔ']
priority_map = {ch: i for i, ch in enumerate(priority_order)}


def rime_sort_key(rime):
    rime = str(rime)

    # 1. 找優先匹配第一個字元的權重
    first = priority_map.get(rime[0], float('inf')) if len(rime) > 0 else float('inf')
    second = priority_map.get(rime[1], float('inf')) if len(rime) > 1 else float('inf')

    # 2. 判斷是否是完全匹配（例如只是一個 "i"）
    full_match_bonus = 0 if rime in priority_order else 1  # 完全匹配的優先

    # 3. 返回三層排序鍵：是否完全匹配 > 第一碼 > 第二碼
    return (full_match_bonus, first, second)


def check_all(xlsx_paths, five=False):
    for path in xlsx_paths:
        print(f"\n==== 檔案: {path} ====")

        try:
            df_xlsx = pd.read_excel(path, dtype=str).fillna('')
        except Exception as e:
            print(f"❌ 無法讀取 Excel 檔案: {path}")
            continue

        # 模糊欄位對應
        column_map = {
            '漢字': ['漢字_程序改名', '單字', '单字', '漢字', 'phrase', '#漢字'],
            '音標': ['IPA_程序改名', 'IPA', 'ipa', '音標', 'syllable'],
            '解釋': ['注釋_程序改名', '注释', '注釋', '解釋', 'notes']
        }

        actual_cols = {}
        for key, candidates in column_map.items():
            for name in candidates:
                if name in df_xlsx.columns:
                    actual_cols[key] = name
                    break

        if '音標' not in actual_cols or '漢字' not in actual_cols:
            print("❌ 找不到音標或漢字欄位")
            continue

        檢查資料格式(df_xlsx, actual_cols['漢字'], actual_cols['音標'], False)

        # 🔁 第一階段：處理自定義編輯指令
        while True:
            edit_input = input("\n✏️ 輸入編輯指令 ，按 Enter 跳過：").strip()
            if not edit_input:
                break
            results, errors = 處理自定義編輯指令(df_xlsx, actual_cols['漢字'], actual_cols['音標'], edit_input)
            for line in results:
                print(line)
            for line in errors:
                print(line)
            if results:
                df_xlsx.to_excel(path, index=False)
                print(f"✅ 已更新 Excel：{path}")
                檢查資料格式(df_xlsx, actual_cols['漢字'], actual_cols['音標'], False)

        # 🔁 第二階段：處理 tone 替換指令
        # 初次顯示調值
        整理並顯示調值(df_xlsx, actual_cols)
        while True:
            user_input = input("\n🔄 輸入替換指令，可用分號分隔多條，按 Enter 跳過此檔案：").strip()
            if not user_input:
                break  # 按 Enter → 處理下一個文件

            commands = [cmd.strip() for cmd in user_input.split(";") if cmd.strip()]
            if len(commands) > 50:
                print("⚠️ 最多一次只能輸入 50 條指令，請拆開來執行")
                continue

            all_updated_rows = []
            valid = True

            for command in commands:
                match = re.match(r"([rs])(\d{1,4})>(\d{1,4})", command)
                if not match:
                    print(f"❌ 無效格式：{command}，請使用類似 r031>3 或 s25>55")
                    valid = False
                    break
                mode, from_tone, to_tone = match.groups()

                updated_rows = []
                for i, row in df_xlsx.iterrows():
                    ipa = row[actual_cols['音標']]
                    hanzi = row[actual_cols['漢字']]
                    match_tone = re.search(r"([0-9¹²³⁴⁵⁶⁷⁸⁹⁰]{1,4})$", str(ipa))
                    if not match_tone:
                        # print(f"⚠️ 指令 {command}：沒有找到可替換的項目")
                        continue

                    tone_raw = match_tone.group(1)
                    tone = tone_raw.translate(SUPER_TO_NORMAL)
                    head = ipa[:-len(tone_raw)]
                    prev_char = head[-1] if head else ""
                    ends_with_ru = prev_char in RU_FINALS

                    if mode == 'r' and ends_with_ru and tone == from_tone:
                        new_ipa = head + to_tone
                        df_xlsx.at[i, actual_cols['音標']] = new_ipa
                        updated_rows.append((hanzi, ipa, new_ipa))

                    elif mode == 's' and not ends_with_ru and tone == from_tone:
                        new_ipa = head + to_tone
                        df_xlsx.at[i, actual_cols['音標']] = new_ipa
                        updated_rows.append((hanzi, ipa, new_ipa))

                if not updated_rows:
                    print(f"⚠️ 指令 {command}：沒有找到可替換的項目")
                else:
                    all_updated_rows.extend(updated_rows)

            if not valid:
                continue  # 格式錯誤，重輸整批

            if not all_updated_rows:
                print("⚠️ 沒有任何替換成功，請重新輸入指令")
                continue

            print(f"\n✅ 替換結果（{len(all_updated_rows)} 條）：")
            for hanzi, old, new in all_updated_rows:
                print(f"{hanzi}\t{old} → {new}")

            df_xlsx.to_excel(path, index=False)
            print(f"✅ 已寫入：{path}")

            # 再次顯示調值
            print("\n📊 當前調值整理：")
            整理並顯示調值(df_xlsx, actual_cols)

        print("🔁開始分別提取聲母韻母")

        # 🔁 第三階段：處理零聲母
        df = extract_all_from_files(path, False, True)
        # print(df)
        # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

        # 過濾声母為 "/" 且韵母以 i/y/u 開頭
        filtered_df = df[(df["声母"] == "/") & (df["韵母"].str.startswith(tuple(["i", "y", "u"])))]

        # 查找點唇齿声母（完全匹配）
        labiodental_onsets = ["w", "v", "ʋ", "ⱱ", "ʷ", "ᵛ", "ᶹ"]
        labiodental_df = df[df["声母"].isin(labiodental_onsets)]

        if not labiodental_df.empty:
            found_labiodentals = labiodental_df["声母"].unique()
            print(f"该點唇齿声母为：{', '.join(found_labiodentals)}")

        # 查找喉塞音声母
        glottal_onsets = ["ʔ", "ˀ", "ø", "(ʔ)", "Ǿ", "∅"]
        glottal_df = df[df["声母"].isin(glottal_onsets)]
        get_j = ["j"]
        get_j_df = df[df["声母"].isin(get_j)]

        if not glottal_df.empty:
            found_onsets = glottal_df["声母"].unique()
            found_rimes = glottal_df["韵母"].unique()
            found_onsets2 = get_j_df["声母"].unique()
            found_rimes2 = get_j_df["韵母"].unique()
            print(f"有喉塞音声母 {', '.join(found_onsets)}，可以与 {', '.join(found_rimes)} 搭配")
            print(f"有硬腭声母 {', '.join(found_onsets2)}，可以与 {', '.join(found_rimes2)} 搭配")
        else:
            print("该表没有对零声母进行处理！")

        # 先保存原始行號（真正保留 df 的 index）
        filtered_df = filtered_df.copy()
        filtered_df["原始行號"] = filtered_df.index

        # 用 sorted 排出正確順序
        sorted_rows = sorted(filtered_df.to_dict("records"), key=lambda row: rime_sort_key(row["韵母"]))

        # 建立排序後 DataFrame，保留原始行號
        filtered_df = pd.DataFrame(sorted_rows).reset_index(drop=True)

        # 顯示排序後結果（不顯示 DataFrame index）
        print(filtered_df)

        # ✏️ 使用者編輯指令介面
        while True:
            edit_input = input("\n✏️ 輸入編輯指令 ，按 Enter 跳過：").strip().replace("\n", "")
            if not edit_input:
                break

            results, errors = 處理批次編輯指令(
                df_xlsx,
                filtered_df,
                actual_cols,
                edit_input
            )

            for line in results:
                print(line)
            for line in errors:
                print(line)

            if results:
                df_xlsx.to_excel(path, index=False)
                print(f"✅ 已更新 Excel：{path}")

                # 重新讀入更新後資料
                df = extract_all_from_files(path, False, True)
                # 查找喉塞音声母
                glottal_onsets = ["ʔ", "ˀ", "ø", "(ʔ)", "Ǿ", "∅"]
                glottal_df = df[df["声母"].isin(glottal_onsets)]
                if not glottal_df.empty:
                    found_onsets = glottal_df["声母"].unique()
                    found_rimes = glottal_df["韵母"].unique()
                    print(f"有喉塞音声母 {', '.join(found_onsets)}，可以与 {', '.join(found_rimes)} 搭配")
                else:
                    print("该表没有对零声母进行处理！")
                # 先保存原始行號（真正保留 df 的 index）
                filtered_df = df[(df["声母"] == "/") & (df["韵母"].str.startswith(tuple(["i", "y", "u"])))]
                filtered_df = filtered_df.copy()
                filtered_df["原始行號"] = filtered_df.index

                # 用 sorted 排出正確順序
                sorted_rows = sorted(filtered_df.to_dict("records"), key=lambda row: rime_sort_key(row["韵母"]))

                # 建立排序後 DataFrame，保留原始行號
                filtered_df = pd.DataFrame(sorted_rows).reset_index(drop=True)
                print(filtered_df)

        # 🔁 第四階段：處理不該出現的聲韻對立
        df = extract_all_from_files(path, False, True)
        # 統計声母與韵母
        print("\n🔢 『声母』統計：")
        print_counts_in_rows(sort_by_custom_order(df["声母"]))
        print("\n🔢 『韵母』統計：")
        print_counts_in_rows(sort_by_custom_order(df["韵母"]))

        while True:
            # 🔍 查詢循環
            user_query = input("\n🔍 輸入要查找的『声母』或『韵母』值（空格分隔，按 Enter 查詢）：").strip()
            if not user_query:
                print("👋 結束查詢。")
                break

            # 支援多個查詢詞
            query_tokens = user_query.split()

            # 在「声母」或「韵母」中匹配任一項
            matched_df = df[
                df["声母"].isin(query_tokens) | df["韵母"].isin(query_tokens)
                ].reset_index().rename(columns={"index": "原始行號"})

            if matched_df.empty:
                print(f"❌ 找不到『{user_query}』相關資料")
                continue

            print("\n📋 查詢結果：")
            print(matched_df)

            edit_input = input("\n✏️ 輸入編輯指令（例如：0~1 y>i），按 Enter 回到查詢：").strip()
            if not edit_input:
                print("🔁 回到查詢介面。")
                continue

            results, errors = 處理批次編輯指令(
                df_xlsx,
                matched_df,
                actual_cols,  # 視你的表格欄位名稱調整
                edit_input
            )

            for line in results:
                print(line)
            for line in errors:
                print(line)

            if results:
                df_xlsx.to_excel(path, index=False)
                print(f"✅ 已更新 Excel：{path}")

                df = extract_all_from_files(path, False, True)
                print("\n🔢 『声母』統計：")
                print_counts_in_rows(sort_by_custom_order(df["声母"]))
                print("\n🔢 『韵母』統計：")
                print_counts_in_rows(sort_by_custom_order(df["韵母"]))

        # 🔁 第五階段：處理出韻字
        if not five:
            continue
        results1 = check_get_chars(df, "声母")
        results2 = check_get_chars(df, "韵母")
        results = results1 + results2
        all_unique_chars = set()
        for result_df in results:
            if not result_df.empty:
                # 提取"對應字"列并将所有字合并到一个集合中
                for chars_list in result_df['對應字']:
                    all_unique_chars.update(chars_list)  # 将每个字添加到集合中

        # 将集合转换为列表，去重后的字将成为列表的元素
        chars_list = list(all_unique_chars)
        # print(chars_list)
        查找出韻字(df_xlsx, actual_cols, chars_list)

        while True:
            edit_input = input("\n✏️ 輸入編輯指令 ，按 Enter 跳過：").strip()
            if not edit_input:
                break
            results, errors = 處理自定義編輯指令(df_xlsx, actual_cols['漢字'], actual_cols['音標'], edit_input)
            for line in results:
                print(line)
            for line in errors:
                print(line)
            if results:
                df_xlsx.to_excel(path, index=False)
                print(f"✅ 已更新 Excel：{path}")
                查找出韻字(df_xlsx, actual_cols, chars_list)


def tsv_to_xlsx(tsv_path, output_path=None):
    if not os.path.exists(tsv_path):
        print(f"[❌] 找不到檔案：{tsv_path}")
        return

    df = pd.read_csv(tsv_path, sep="\t", dtype=str)

    if output_path is None:
        output_path = os.path.splitext(tsv_path)[0] + ".xlsx"

    df.to_excel(output_path, index=False)
    print(f"[✅] 轉換完成：{output_path}")


def main(mode='onl'):
    root = tk.Tk()
    root.withdraw()
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)

    five = True

    if mode == 'only':
        xlsx_paths = filedialog.askopenfilenames(
            title="選擇多個 Excel 文件",
            filetypes=[("Excel Files", "*.xlsx")]
        )
        check_all(xlsx_paths)
    else:
        file_paths = filedialog.askopenfilenames(
            title="選擇文件",
            filetypes=[
                ("支持格式", "*.xlsx *.xls *.doc *.docx *.tsv"),
                ("Excel 文件", "*.xlsx *.xls"),
                ("Word 文件", "*.doc *.docx"),
                ("TSV 文件", "*.tsv"),
                ("所有文件", "*.*")
            ]
        )
        column_map = {
            '漢字': ['漢字_程序改名', '單字', '单字', '漢字', 'phrase', '#漢字'],
            '音標': ['IPA_程序改名', 'IPA', 'ipa', '音標', 'syllable'],
            '解釋': ['注釋_程序改名', '注释', '注釋', '解釋', 'notes']
        }
        print(file_paths)
        for path in file_paths:
            ext = os.path.splitext(path)[1].lower()
            if ext == ".tsv":
                tsv_to_xlsx(path, path)
            elif ext in (".doc", ".docx"):
                process_縣志_word(path, level=1)
                tsv_path = os.path.splitext(path)[0] + ".tsv"
                if os.path.exists(tsv_path):
                    xlsx_path = os.path.splitext(path)[0] + ".xlsx"
                    tsv_to_xlsx(tsv_path, xlsx_path)
                    check_all([xlsx_path], five)

            elif ext in (".xlsx", ".xls"):
                try:
                    df = pd.read_excel(path, dtype=str)
                except Exception as e:
                    print(f"[❌] 無法讀取：{path}\n原因：{e}")
                    continue

                df_cols = df.columns.tolist()

                mapped_cols = {}
                for std_col, variants in column_map.items():
                    for v in variants:
                        if v in df_cols:
                            mapped_cols[std_col] = v
                            break

                # 如果三個標準欄位都找到，就 rename 並執行 check_all
                if set(mapped_cols.keys()) >= {"漢字", "音標", "解釋"}:
                    # df = df.rename(columns={v: k for k, v in mapped_cols.items()})
                    check_all([path], five)
                else:
                    required_cols = ["漢字", "音標", "解釋"]
                    print(mapped_cols)
                    missing = [col for col in required_cols if col not in mapped_cols]
                    if missing:
                        print(f"❌ 缺少欄位：{missing}，是否為縣志/跳跳老鼠格式？")
                        print("若是跳跳老鼠，請輸入1\n若是縣志，請輸入2")
                        while True:
                            user_input = input("請輸入 (1 或 2)：").strip()
                            if user_input == "1":
                                print("👉 使用跳跳老鼠格式邏輯")
                                process_跳跳老鼠(path, level=1)
                                tsv_path = os.path.splitext(path)[0] + ".tsv"
                                if os.path.exists(tsv_path):
                                    xlsx_path = os.path.splitext(path)[0] + "pro" + ".xlsx"
                                    tsv_to_xlsx(tsv_path, xlsx_path)
                                    check_all([xlsx_path], five)
                                break
                            elif user_input == "2":
                                print("👉 使用縣志格式邏輯")
                                process_縣志_excel(path, level=1)
                                tsv_path = os.path.splitext(path)[0] + ".tsv"
                                if os.path.exists(tsv_path):
                                    xlsx_path = os.path.splitext(path)[0] + "pro" + ".xlsx"
                                    tsv_to_xlsx(tsv_path, xlsx_path)
                                    check_all([xlsx_path], five)
                                break
                            else:
                                print("⚠️ 請輸入正確的數字（1 或 2）")


if __name__ == "__main__":
    main()
