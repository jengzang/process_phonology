import sqlite3
import pandas as pd

from source.config import DIALECTS_DB_PATH, CHARACTERS_DB_PATH
from source.process_input import split_pho_input, match_locations_batch, query_dialect_abbreviations

"""
整體流程總結：

1. 使用者給定地點（locations）、語音特徵（features，例如聲母、韻母）與分組欄位（status_inputs，例如"聲組"）

2. run_dialect_analysis：
   - 解析使用者指定的分組欄位，建立每個特徵對應的 group_fields
   - 調用 query_dialect_features 查詢每個地點與特徵對應的漢字子表 sub_df
   - 對每組漢字調用 analyze_characters_from_db 進行實際分組與統計

3. analyze_characters_from_db：
   - 從 characters.db 查出指定漢字的語音屬性
   - 根據 group_fields 進行分組
   - 計算字數、佔比、多地位簡表，並統整為結果

4. 返回的資料可以用來分析語音特徵在不同地點的分布狀況與音系特點
"""


def query_dialect_features(locations, features, db_path=DIALECTS_DB_PATH, table="dialects"):
    """
    從 dialects 數據庫中查出指定地點與特徵（如聲母、韻母等）對應的漢字。

    返回格式為：
    {
        '聲母': {
            'b': {
                '漢字': [...],
                'sub_df': 子表 DataFrame（含簡稱、漢字、特徵值、音節、是否多音字）,
                '多音字詳情': [hz1:pron1;pron2, hz2:pron1;pron2]
            },
            ...
        },
        '韻母': {
            ...
        }
    }
    """
    # 連接資料庫
    print(f"📦 連接資料庫：{db_path}")
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    conn.close()
    print(f"✅ 資料總筆數：{len(df)}")

    # 過濾輸入的地點
    df = df[df["簡稱"].isin(locations)]

    result = {}

    for feature in features:
        sub_df = df[["簡稱", "漢字", feature, "音節", "多音字"]].dropna(subset=[feature])
        feature_dict = {}

        for value in sorted(sub_df[feature].unique()):
            # 找出所有對應的漢字
            chars = sub_df[sub_df[feature] == value]["漢字"].unique().tolist()
            feature_dict[value] = {
                "漢字": chars,
                "sub_df": sub_df[(sub_df[feature] == value)],
                "多音字詳情": []
            }

            # 多音字查詢
            for loc in locations:
                poly_df = sub_df[(sub_df["多音字"] == "1") & (sub_df["簡稱"] == loc) & (sub_df[feature] == value)]
                for hz in poly_df["漢字"].unique():
                    all_pron = df[(df["漢字"] == hz) & (df["簡稱"] == loc)]["音節"].unique().tolist()
                    detail = f"{hz}:{';'.join(all_pron)}"
                    feature_dict[value]["多音字詳情"].append(detail)

        result[feature] = feature_dict

    return result


def analyze_characters_from_db(
        char_list,
        feature_type,
        feature_value,
        loc,
        sub_df,
        char_db_path=CHARACTERS_DB_PATH,
        group_fields=None
):
    """
    根據漢字名單，從 characters.db 中查出相關音系特徵資料，並根據指定的 group_fields 欄位分組統計。

    分組後每組返回：
    - 該組對應的字（已去重）
    - 字數與佔比（以去重後字數為準）
    - 多地位詳情（保留原始重複資料，用於展示）
    - 分組值（欄位對應值，例如 {'調': '平', '清濁': '全濁'}）

    若 group_fields 為空，根據特徵類型自動選擇預設欄位：
        聲母 ➜ 聲
        韻母 ➜ 韻
        聲調 ➜ 清濁 + 調
    """

    default_grouping = {
        "聲母": ["聲"],
        "韻母": ["韻"],
        "聲調": ["清濁", "調"]
    }

    if not group_fields:
        group_fields = default_grouping.get(feature_type)
        if not group_fields:
            raise ValueError(f"❌ 未定義的 feature_type：{feature_type}")

    conn = sqlite3.connect(char_db_path)
    placeholders = ','.join(['?'] * len(char_list))
    query = f"SELECT * FROM characters WHERE 漢字 IN ({placeholders})"
    df = pd.read_sql_query(query, conn, params=char_list)
    conn.close()

    for col in ["攝", "呼", "等", "韻", "調", "系", "組", "聲", "多地位標記"]:
        if col not in df.columns:
            df[col] = None

    total_chars = len(set(sub_df["漢字"]))
    grouped_result = []

    df = df.dropna(subset=group_fields)
    grouped = df.groupby(group_fields)

    for group_keys, group_df in grouped:
        if isinstance(group_keys, (list, tuple)):
            group_values = dict(zip(group_fields, group_keys))
        else:
            group_values = dict(zip(group_fields, [group_keys]))

        unique_chars = group_df["漢字"].unique().tolist()
        count = len(unique_chars)

        poly_details = []
        poly_df = group_df[group_df["多地位標記"] == "1"]
        for hz in poly_df["漢字"].unique():
            sub = poly_df[poly_df["漢字"] == hz]
            summary = []
            for _, row in sub.iterrows():
                parts = f"{row['攝']}{row['呼']}{row['等']}{row['韻']}{row['調']}"
                meta = f"{row['系']}(系){row['組']}(組){row['聲']}(母)"
                summary.append(f"{parts},{meta}")
            poly_details.append(f"{hz}: {' | '.join(summary)}")

        grouped_result.append({
            "地點": loc,
            "特徵類別": feature_type,
            "特徵值": feature_value,
            "分組值": group_values,
            "字數": count,
            "佔比": round(count / total_chars, 4) if total_chars else 0,
            "對應字": unique_chars,
            "多地位詳情": "; ".join(poly_details)
        })

    return grouped_result


def pho2sta(locations, regions, features, status_inputs,
            pho_values=None,
            dialect_db_path=DIALECTS_DB_PATH,
            character_db_path=CHARACTERS_DB_PATH):
    """
       新增參數 pho_values：若非空，僅處理在其中的 feature_value，否則處理全部。
       若 pho_values 沒有任何值在資料中出現，則 fallback 輸出所有。
    """

    HIERARCHY_COLUMNS = ["攝", "呼", "等", "韻", "入", "調", "清濁", "系", "組", "聲"]
    pho_values = split_pho_input(pho_values or [])

    grouping_columns_map = {}
    for idx, feature in enumerate(features):
        user_input = status_inputs[idx] if idx < len(status_inputs) else ""
        user_columns = [col for col in HIERARCHY_COLUMNS if col in user_input]
        if not user_columns:
            print(f"⚠️ 無有效欄位於輸入「{user_input}」中 → 將使用 analyze_characters_from_db 的預設分組欄位")
            grouping_columns_map[feature] = None
        else:
            print(f"[DEBUG] 特徵 {feature} 使用分組欄位：{user_columns}")
            grouping_columns_map[feature] = user_columns

    locations_new = query_dialect_abbreviations(regions, locations)
    # 驗證地點
    match_results = match_locations_batch(" ".join(locations_new))
    if not any(res[1] == 1 for res in match_results):
        print("🛑 沒有任何地點完全匹配，終止分析。")
        return []

    unique_abbrs = list({abbr for res in match_results for abbr in res[0]})
    print(f"\n📍 完全匹配地點簡稱：{unique_abbrs}")

    results = []
    dialect_output = query_dialect_features(unique_abbrs, features, db_path=dialect_db_path)

    for loc in unique_abbrs:
        for feature in features:
            group_fields = grouping_columns_map.get(feature)

            feature_items = dialect_output[feature].items()

            # 若 pho_values 非空，先過濾出存在的
            if pho_values:
                filtered_items = [(fv, d) for fv, d in feature_items if fv in pho_values]
                # 若沒有任何一個 match，就 fallback 為全部
                if filtered_items:
                    feature_items = filtered_items

            for feature_value, data in feature_items:
                sub_df = data["sub_df"]
                loc_chars = sub_df[sub_df["簡稱"] == loc]["漢字"].unique().tolist()
                if not loc_chars:
                    continue

                result = analyze_characters_from_db(
                    char_list=loc_chars,
                    feature_type=feature,
                    feature_value=feature_value,
                    loc=loc,
                    sub_df=sub_df[sub_df["簡稱"] == loc],
                    char_db_path=character_db_path,
                    group_fields=group_fields,
                )

                results.extend(result if isinstance(result, list) else [result])

    return results


if __name__ == "__testp2s__":
    locations = ['东莞莞城 順德大良', '雲浮富林']
    features = ['聲母', '韻母', '聲調']
    group_inputs = ['組聲', '攝等', '清濁調']  # ✅ 用戶指定分組欄位
    pho_value = ['l', 'm', 'an']
    regions = ['封綏', '儋州']
    results = pho2sta(locations, regions, features, group_inputs, pho_value)

    for row in results:
        print(row)
