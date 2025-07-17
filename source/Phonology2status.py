import sqlite3
import pandas as pd

from source.config import DIALECTS_DB_PATH, CHARACTERS_DB_PATH

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
    - 分組值（如：山合三仙上）
    - 該組對應的字
    - 字數與佔比
    - 多地位詳情（簡潔格式：卷: 山合三仙上,見(系)見(組)見(聲)）

    若 group_fields 為空，根據特徵類型自動選擇預設欄位：
        聲母 ➜ 聲
        韻母 ➜ 韻
        聲調 ➜ 清濁 + 調
    """
    # ✅ 預設分組欄位（僅在 group_fields 未傳入時才用）
    default_grouping = {
        "聲母": ["聲"],
        "韻母": ["韻"],
        "聲調": ["清濁", "調"]
    }

    if not group_fields:
        group_fields = default_grouping.get(feature_type)
        if not group_fields:
            raise ValueError(f"❌ 未定義的 feature_type：{feature_type}")

    # 連接並查詢 characters.db
    conn = sqlite3.connect(char_db_path)
    placeholders = ','.join(['?'] * len(char_list))
    query = f"SELECT * FROM characters WHERE 漢字 IN ({placeholders})"
    df = pd.read_sql_query(query, conn, params=char_list)
    conn.close()

    # 確保欄位齊全
    for col in ["攝", "呼", "等", "韻", "調", "系", "組", "聲", "多地位標記"]:
        if col not in df.columns:
            df[col] = None

    total_chars = len(sub_df["漢字"].unique())
    grouped_result = []

    # 依據 group_fields 分組（先去除有缺漏的）
    df = df.dropna(subset=group_fields)
    grouped = df.groupby(group_fields)

    for group_keys, group_df in grouped:
        # 統一為列表
        if isinstance(group_keys, str):
            group_keys = [group_keys]
        # print(f"[DEBUG] 分組欄位: {group_fields} → 分組值: {group_keys}")

        group_label = "-".join(str(k) for k in group_keys)
        feature_chars = group_df["漢字"].unique().tolist()
        count = len(feature_chars)

        # 多地位簡化格式
        poly_details = []
        poly_df = group_df[group_df["多地位標記"] == "1"]
        for hz in poly_df["漢字"].unique():
            sub = group_df[group_df["漢字"] == hz]
            summary = []
            for _, row in sub.iterrows():
                parts = f"{row['攝']}{row['呼']}{row['等']}{row['韻']}{row['調']}"
                meta = f"{row['系']}(系){row['組']}(組){row['聲']}(聲)"
                summary.append(f"{parts},{meta}")
            poly_details.append(f"{hz}: {' | '.join(summary)}")

        grouped_result.append({
            "地點": loc,
            "特徵類別": feature_type,
            "特徵值": feature_value,
            "分組值": group_label,
            "分組欄位": group_fields,
            "字數": count,
            "佔比": round(count / total_chars, 4) if total_chars else 0,
            "對應字": feature_chars,
            "多地位詳情": "; ".join(poly_details)
        })

    return grouped_result


def pho2sta(locations, features, status_inputs,
            dialect_db_path=DIALECTS_DB_PATH,
            character_db_path=CHARACTERS_DB_PATH):
    """
       主控函數。

       功能：
       - 從 dialects 資料庫中查詢指定地點和特徵的漢字（透過 query_dialect_features）
       - 根據用戶指定的分組欄位 status_inputs，控制每個特徵的 group_fields
       - 呼叫 analyze_characters_from_db 完成統計與分組

       備註：
       - 若用戶輸入不合法（不在 HIERARCHY_COLUMNS 中），會使用 analyze_characters_from_db 預設欄位
       - 支援多地點、每個特徵值在每個地點分開統計
       """

    HIERARCHY_COLUMNS = ["攝", "呼", "等", "韻", "入", "調", "清濁", "系", "組", "聲"]

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

    results = []
    dialect_output = query_dialect_features(locations, features, db_path=dialect_db_path)

    for loc in locations:
        for feature in features:
            group_fields = grouping_columns_map.get(feature)
            for feature_value, data in dialect_output[feature].items():
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
                    group_fields=group_fields
                )

                results.extend(result if isinstance(result, list) else [result])

    return results


locations = ['東莞莞城', '雲浮富林']
features = ['聲母', '韻母', '聲調']
status_inputs = ['組聲', '韻等', '清濁調']  # ✅ 用戶指定分組欄位，合法或不合法皆支援

results = pho2sta(locations, features, status_inputs)

for row in results:
    print(row)
