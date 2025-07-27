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

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # 添加项目根目录到 sys.path
from check.maybe_error_chars import check_get_chars
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
            "ɑɐɒɓʙβɔɕçðɖɗɘəɚɛɜɞɟʄɡɢʛɣʰɥʜɦɪʝɭɬɫʟɮɰɱɲɳɴɵøœɶɸɹɻʁʀɽɾʃʂʈʊʋʌʍχʎʑʐʒʔʕʡʢʘʞθʼˈˌːˑ⁰¹²³⁴⁵⁶⁷⁸⁹ⁿˡʲʳˀ"
            "ʦʧʨʂʐʑʒʮʰʲː˞ˠˤ̩̯̝̞̤̰̹̻̃̍̽̚=~^"
            "ıſɩɷʅɥʯεɝɚᴇãẽĩỹõúαᵘᶷᶤᶶᵚʸᶦᵊⁱ◌∅"
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

        if any(sep in ipa for sep in ",.;'/=-"):
            parts = re.split(r"[,\.;'/=\-]", ipa)
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


def 查找出韻字(df_xlsx, actual_cols, chars_list):
    # 查找并输出指定的漢字的讀音
    print("\n📝 以下字可能有誤（出韻）：")
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


def main():
    root = tk.Tk()
    root.withdraw()

    xlsx_paths = filedialog.askopenfilenames(
        title="選擇多個 Excel 文件",
        filetypes=[("Excel Files", "*.xlsx")]
    )

    for path in xlsx_paths:
        print(f"\n==== 檔案: {path} ====")

        try:
            df_xlsx = pd.read_excel(path, dtype=str).fillna('')
        except Exception as e:
            print(f"❌ 無法讀取 Excel 檔案: {path}")
            continue

        # 模糊欄位對應
        column_map = {
            '漢字': ['漢字_程序改名', '單字', '单字', '漢字', 'phrase'],
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

        df = extract_all_from_files(path)
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

        # 🔁 第三階段：處理出韻字
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


if __name__ == "__main__":
    main()
