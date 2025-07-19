import sqlite3
import pandas as pd
import re
from source.process_input import auto_convert_batch, match_locations_batch, query_dialect_abbreviations
from source.config import CHARACTERS_DB_PATH, DIALECTS_DB_PATH

"""
本腳本提供一組函數用於從語音描述詞查詢對應漢字，並根據不同地點與語音特徵進行統計分析。
核心流程與功能如下：

1. run_status：
   ➤ 將使用者輸入（如「知組三」）解析為篩選語法並查詢 characters.db，回傳漢字與多地位字。

2. query_characters_by_path：
   ➤ 支援解析 [值]{欄位} 語法，執行資料庫查詢並判定多地位。

3. query_by_status：
   ➤ 根據查得漢字，在指定地點與語音特徵下計算統計資訊與多音字詳情。

4. run_feature_analysis：
   ➤ 整合 run_status 與 query_by_status，批次處理多組輸入與地點，進行完整分析流程。

"""


# 可用於分層篩選的欄位
HIERARCHY_COLUMNS = ["攝", "呼", "等", "韻", "入", "調", "清濁", "系", "組", "聲"]


def query_characters_by_path(path_string, db_path=CHARACTERS_DB_PATH, table="characters"):
    """
    📌 根據用戶輸入語法（如 "[知]{組}[三]{等}"）從 characters.db 中查出符合條件的漢字。

    功能包含：
    - 解析語法中指定的「欄位 + 值」條件
    - 根據條件篩選出符合的漢字
    - 額外分析這些字是否為「多地位」字（即一字多個音系地位）

    回傳：
    - 符合條件的漢字清單
    - 多地位的漢字清單
    """

    print(f"\n📥 查詢語法輸入：{path_string}")

    # 解析語法：[值]{欄位}
    pattern = r"\[([^\[\]]+)\]\{([^\{\}]+)\}"
    matches = re.findall(pattern, path_string)

    if not matches:
        print("❌ 無法解析輸入語法。請使用 [值]{欄位} 的格式")
        return [], []

    print(f"🔍 解析出的條件：{matches}")

    filter_columns = [col for _, col in matches]
    for col in filter_columns:
        if col not in HIERARCHY_COLUMNS:
            print(f"⚠️ 欄位「{col}」不在允許的層級欄位中")
            return [], []

    # 讀取資料
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    conn.close()

    # 執行篩選
    filtered_df = df.copy()
    for value, column in matches:
        before = len(filtered_df)
        filtered_df = filtered_df[filtered_df[column] == value]
        after = len(filtered_df)
        print(f"🔽 篩選 {column} = {value}：剩下 {after} 筆（原本 {before} 筆）")
        if after == 0:
            return [], []

    # 提取漢字
    if "漢字" not in filtered_df.columns:
        print("❌ 缺少「漢字」欄")
        return [], []

    characters = filtered_df["漢字"].dropna().tolist()
    print(f"\n🎯 符合條件的漢字共 {len(characters)} 個")

    # 多地位過濾（優化判斷）
    multi_chars = []
    if "多地位標記" in filtered_df.columns:
        candidates = filtered_df[
            filtered_df["多地位標記"] == "1"
            ]["漢字"].dropna().unique().tolist()

        print(f"🟡 初步多地位標記候選：{len(candidates)} 字")

        for word in candidates:
            all_rows = df[df["漢字"] == word]
            sub = all_rows[filter_columns].drop_duplicates()
            if len(sub) > 1:
                multi_chars.append(word)

        print(f"🟠 經過比對後確定有多地位的漢字：{len(multi_chars)} 字")
    else:
        print("⚠️ 無「多地位標記」欄")

    return characters, multi_chars


def query_by_status(char_list, locations, features, user_input, db_path=DIALECTS_DB_PATH, table="dialects"):
    """
    📌 根據提供的漢字名單，查詢其在不同地點與語音特徵（如聲母/韻母）下的分佈情況。

    功能包含：
    - 從 dialects.db 中找出指定地點與漢字的資料
    - 計算每種語音特徵值（如 b, p, m...）的字數、比例（去重後）
    - 處理「多音字」的詳細音節資訊（保留所有對應的發音）
    - 輸出欄位包含：分組值（特徵=值）

    回傳：
    - 每筆統計結果以字典方式輸出，最終轉為 DataFrame
    """
    print(f"📦 連接資料庫：{db_path}")
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    conn.close()
    print(f"✅ 資料總筆數：{len(df)}")

    results = []

    for loc in locations:
        print(f"\n🔍 處理地點：{loc}")
        loc_df = df[df["簡稱"] == loc]
        print(f"   - 該地資料筆數：{len(loc_df)}")

        loc_chars_df = loc_df[loc_df["漢字"].isin(char_list)]
        print(f"   - 匹配輸入漢字筆數：{len(loc_chars_df)} / {len(char_list)}")

        if loc_chars_df.empty:
            print("   ⚠️ 無符合漢字，略過此地點")
            results.append({
                "地點": loc,
                "特徵類別": "無",
                "特徵值": "無",
                "分組值": {},
                "字數": 0,
                "佔比": 0.0,
                "對應字": [],
                "多音字詳情": "❌ 無符合漢字"
            })
            continue

        total_chars = len(loc_chars_df["漢字"].unique())

        for feature in features:
            # print(f"   🔎 特徵欄位：{feature}")
            feature_groups = loc_chars_df.groupby(feature)

            for fval, sub_df in feature_groups:
                all_chars = sub_df["漢字"].tolist()
                unique_chars = list(set(all_chars))
                count = len(unique_chars)

                # print(f"     ▶︎ {feature} = {fval}，字數：{count}，字例：{unique_chars[:5]}...")

                poly_df = sub_df[sub_df.get("多音字") == "1"]
                poly_details = []

                for hz in poly_df["漢字"].unique():
                    all_pron = df[(df["漢字"] == hz) & (df["簡稱"] == loc)]["音節"].unique().tolist()
                    # print(f"       ⤷ 多音字：{hz}，音節：{all_pron}")
                    poly_details.append(f"{hz}:{'|'.join(all_pron)}")

                results.append({
                    "地點": loc,
                    "特徵類別": feature,
                    "特徵值": user_input,
                    "分組值": {user_input: fval},  # 將 user_input 加入分組值
                    "字數": count,
                    "佔比": round(count / total_chars, 4) if total_chars else 0.0,
                    "對應字": unique_chars,
                    "多音字詳情": "; ".join(poly_details) if poly_details else ""
                })

    print("\n✅ 分析完成！")
    return pd.DataFrame(results)



def run_status(
        input_strings,
        db_path=CHARACTERS_DB_PATH,
        table="characters"
):
    """
    📌 功能總結：

    🔹 主要用途：對使用者輸入的一組「音系條件語法」（例如：「知組三」、「通开三」）進行格式化轉換，
    並查詢 characters.db 中，符合該條件的所有漢字。

    ✔ 處理流程：
    1. 調用 `auto_convert_batch` → 將輸入轉換為標準語法格式（如 [知]{組}[三]{等}）
    2. 每個轉換結果，丟給 `query_characters_by_path`：
       - 查出符合條件的漢字列表
       - 判定哪些是多地位的字（例如：一字多組合、具備多重地位）
    3. 整合每個輸入的查詢結果，包含：
       - 原始輸入
       - 查得的漢字清單
       - 多地位漢字清單

    🔁 多筆輸入可以批次處理，適合在主流程中被呼叫，例如：
       run_status(["知組三", "通开三"])
       → 傳回所有符合這些條件的字，以及它們的多地位判定結果。

    🔄 它是 run_feature_analysis 的「前處理步驟」，提供：
       ➤ 字集清單（char_list）
       ➤ 多地位字清單（multi_chars）
    """

    results_summary = []

    for s in input_strings:
        print(f"\n🔹 測試輸入：{s}")
        batch_result = auto_convert_batch(s)
        print(f"  🧪 auto_convert_batch ➤ {batch_result}")

        if not isinstance(batch_result, list):
            results_summary.append((s, False, False))
            print(f"  ❌ 無法處理（非 list 結果）：{s}")
            continue

        has_error = any(
            isinstance(r, tuple) and r[0] is False for r in batch_result
        )

        # 嘗試處理成功的部分
        all_chars = []
        all_multi = []
        for path_tuple in batch_result:
            if isinstance(path_tuple, tuple) and path_tuple[0] is not False:
                path_str = path_tuple[0]
                characters, multi_chars = query_characters_by_path(
                    path_str, db_path=db_path, table=table
                )
                all_chars.extend(characters)
                all_multi.extend(multi_chars)

        if all_chars:
            results_summary.append((s, all_chars, list(set(all_multi))))
        else:
            results_summary.append((s, False, False))

        if has_error:
            print(f"  ⚠️ 部分片段轉換失敗：{s}")

    return results_summary


def sta2pho(
        locations,
        regions,
        features,
        test_inputs,
        db_path_char=CHARACTERS_DB_PATH,
        db_path_dialect=DIALECTS_DB_PATH
):
    """
    📌 主控函數：對語音條件輸入進行特徵分析，支援多地點與特徵欄位。

    返回值：
    List of dicts，每個 dict 含：
        {
            "輸入條件": ...,     # 原始語音條件，如「知組三」
            "對應字": [...],     # 符合條件的漢字
            "多地位字": [...],   # 多地位的漢字
            "統計結果": DataFrame # 每地點+特徵的統計
        }
    """
    locations_new = query_dialect_abbreviations(regions, locations)
    # 驗證地點
    match_results = match_locations_batch(" ".join(locations_new))
    if not any(res[1] == 1 for res in match_results):
        print("🛑 沒有任何地點完全匹配，終止分析。")
        return []

    unique_abbrs = list({abbr for res in match_results for abbr in res[0]})
    print(f"\n📍 完全匹配地點簡稱：{unique_abbrs}")

    # ➕ 若 test_inputs 為空，自動根據 features 推導測試條件
    if not test_inputs:
        print("ℹ️ test_inputs 為空，自動推導條件字串...")
        conn = sqlite3.connect(db_path_char)
        df_char = pd.read_sql_query("SELECT * FROM characters", conn)
        conn.close()

        auto_inputs = []
        auto_features = []

        for feat in features:
            if feat == "聲母":
                unique_vals = sorted(df_char["聲"].dropna().unique())
                auto_inputs.extend([f"{v}母" for v in unique_vals])
                auto_features.extend(["聲母"] * len(unique_vals))

            elif feat == "韻母":
                unique_vals = sorted(df_char["攝"].dropna().unique())
                auto_inputs.extend([f"{v}攝" for v in unique_vals])
                auto_features.extend(["韻母"] * len(unique_vals))

            elif feat == "聲調":
                clean_vals = sorted(df_char["清濁"].dropna().unique())
                tone_vals = sorted(df_char["調"].dropna().unique())

                for cv in clean_vals:
                    for tv in tone_vals:
                        auto_inputs.append(f"{cv}{tv}")
                        auto_features.append("聲調")

            else:
                print(f"⚠️ 未支援的特徵類型：{feat}，略過")

        test_inputs = auto_inputs
        features = auto_features

        print(f"🔧 產生輸入條件 {len(test_inputs)} 筆 ➤ 前5項：{test_inputs[:5]}")


    if len(features) == 1:
        # 如果只有一個 feature，將所有 test_inputs 與該唯一 feature 對應
        all_results = []
        for user_input in test_inputs:
            print("\n" + "═" * 60)
            print(f"📘 分析輸入：{user_input} 對應特徵：{features[0]}")

            summary = run_status([user_input], db_path=db_path_char)

            for path_input, chars, multi in summary:
                print(f"\n📘 輸入原文：{path_input}")
                if chars is False:
                    print("🛑 查詢失敗或無法解析")
                    continue

                # print(f"🔡 查得字數：{len(chars)} ➤ {chars}")
                # print(f"⚠️ 多地位：{multi if multi else '無'}")

                all_chars = list(set(chars))

                print(f"\n🔧 開始分析『{user_input}』的特徵分布 ({features[0]})...\n")
                df = query_by_status(all_chars, unique_abbrs, [features[0]], user_input, db_path=db_path_dialect)

                all_results.append(df)
    else:
        # 如果 features 有多個元素，正常的 zip 對應
        all_results = []
        for user_input, feature in zip(test_inputs, features):
            # print("\n" + "═" * 60)
            print(f"📘 分析輸入：{user_input} 對應特徵：{feature}")

            summary = run_status([user_input], db_path=db_path_char)

            for path_input, chars, multi in summary:
                print(f"\n📘 輸入原文：{path_input}")
                if chars is False:
                    print("🛑 查詢失敗或無法解析")
                    continue

                print(f"🔡 查得字數：{len(chars)} ➤ {chars}")
                print(f"⚠️ 多地位：{multi if multi else '無'}")

                all_chars = list(set(chars))

                print(f"\n🔧 開始分析『{user_input}』的特徵分布 ({feature})...\n")
                df = query_by_status(all_chars, unique_abbrs, [feature], user_input, db_path=db_path_dialect)

                all_results.append(df)

    return all_results



# 這函數沒啥用
def extract_unique_values(db_path=CHARACTERS_DB_PATH, table="characters"):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    conn.close()

    unique_values = {}

    for col in HIERARCHY_COLUMNS:
        if col in df.columns:
            values = df[col].dropna().unique()
            values = sorted(str(v).strip() for v in values if str(v).strip() != "")
            unique_values[col] = values
        else:
            unique_values[col] = []
            print(f"⚠️ 欄位「{col}」不存在")

    return unique_values


# if __name__ == "__main__":
#     pd.set_option('display.max_rows', None)
#     pd.set_option('display.max_columns', None)
#     pd.set_option('display.max_colwidth', None)
#     pd.set_option('display.width', 0)
#
#     status_inputs = [
#         "知組三 端",
#         "通开三",
#     ]
#     # status_inputs = [
#     # ]
#     locations = ['东莞莞城', '雲浮富林']
#     # features = ['聲母', '韻母', '聲調']
#     regions = ['封綏', '儋州']
#     features = ['韻母']
#
#     results = sta2pho(locations, regions, features, status_inputs)
#     # print(all_summaries)
#
#     for row in results:
#         print(row)