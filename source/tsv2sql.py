import os
import sqlite3
from pathlib import Path

import pandas as pd

from source.change_coordinates import bd09togcj02
from source.config import HAN_PATH, APPEND_PATH, QUERY_DB_PATH, DIALECTS_DB_PATH, CHARACTERS_DB_PATH, PHO_TABLE_PATH
from source.get_new import extract_all_from_tsv
from source.match_fromdb import get_tsvs


def build_dialect_database():
    han_file = Path(HAN_PATH)  # 使用固定路徑
    other_file = Path(APPEND_PATH)
    sqlite_db = Path(QUERY_DB_PATH)

    # --- 欄位對應 ---
    tone_map = {
        "[1]陰平": "T1陰平",
        "[2]陽平": "T2陽平",
        "[3]陰上": "T3陰上",
        "[4]陽上": "T4陽上",
        "[5]陰去": "T5陰去",
        "[6]陽去": "T6陽去",
        "[7]陰入": "T7陰入",
        "[8]陽入": "T8陽入",
        "[9]其他調": "T9其他調",
        "[10]輕聲": "T10輕聲"
    }

    geo_map = {
        "省/自治區/直轄市": "省",
        "地區/市/州": "市",
        "縣/市/區": "縣",
        "鄕/鎭/街道": "鎮",
        "村/社區/居民點": "行政村",
        "自然村": "自然村"
    }

    rename_map = {**tone_map, **geo_map}

    # 欄位清單（原始名稱）
    required_columns = [
        "語言", "簡稱", "音典排序", "音典分區", "字表來源（母本）", "方言島",
        "存儲標記", "經緯度", "地圖級別",
        *geo_map.keys(),
        *tone_map.keys()
    ]

    # --- 讀取 Append_files.xlsx.xlsx ---
    df_other = pd.read_excel(other_file, sheet_name="檔案", header=0)
    df_other.columns = df_other.columns.str.strip()
    df_other["存儲標記"] = ""  # ✅ 補上這一列
    df_other = df_other[[col for col in required_columns if col in df_other.columns]].copy()
    df_other = df_other.rename(columns=rename_map)

    # --- 讀取 漢字音典表，跳過第 2 行（即 index 0）---
    df_han = pd.read_excel(han_file, sheet_name="檔案", header=0)
    df_han = df_han.drop(index=0).reset_index(drop=True)
    df_han.columns = df_han.columns.str.strip()
    df_han["存儲標記"] = ""  # ✅ 補上這一列
    df_han = df_han[[col for col in required_columns if col in df_han.columns]].copy()
    df_han = df_han.rename(columns=rename_map)

    # --- 處理經緯度轉換 ---
    def convert_coordinates(df):
        """
        對 '經緯度' 列進行坐標轉換，忽略空值
        """
        new_coordinates = []
        for coords in df['經緯度']:
            # 如果經緯度為空，跳過
            if pd.isna(coords) or coords.strip() == '':
                new_coordinates.append(None)  # 如果是空值，將經緯度設為 None
                continue

            # 確保 coords 是字符串類型
            coords = str(coords).strip()

            # 分割經緯度
            bd_lon, bd_lat = map(float, coords.split(','))

            # 使用轉換函數
            converted_coords = bd09togcj02(bd_lon, bd_lat)
            new_coordinates.append(f"{converted_coords[0]},{converted_coords[1]}")  # 轉換後的坐標以逗號分隔

        # 更新 '經緯度' 列
        df['經緯度'] = new_coordinates
        return df

    # 處理 df_other 和 df_han 兩個 DataFrame
    df_other = convert_coordinates(df_other)
    df_han = convert_coordinates(df_han)

    # --- 寫入 SQLite ---
    with sqlite3.connect(sqlite_db) as conn:
        # 記錄來源
        df_other["_來源"] = "Append_files.xlsx"
        df_han["_來源"] = "漢字音典表"

        # 合併資料
        merged = pd.concat([df_other, df_han], ignore_index=True)

        # 轉換 required_columns → 重命名後的欄位名
        renamed_required_columns = [rename_map.get(col, col) for col in required_columns]

        # 計算非空欄位數
        merged["_non_null_count"] = merged[renamed_required_columns].notna().sum(axis=1)

        # 優先來源標記（漢字音典表優先）
        merged["_來源優先"] = merged["_來源"].apply(lambda x: 1 if x == "漢字音典表" else 0)

        # 最終保留資料列表
        final_rows = []
        print("\n📊 重複簡稱選擇詳情如下：")
        for name, group in merged.groupby("簡稱"):
            if len(group) > 1:
                group = group.sort_values(by=["_non_null_count", "_來源優先"], ascending=[False, False])
                selected = group.iloc[0]
                final_rows.append(selected)

                def get_nonnull_info(row):
                    if row.empty:
                        return 0, []
                    count = int(row["_non_null_count"])
                    cols = [col for col in renamed_required_columns if pd.notna(row[col]) and row[col] != ""]
                    return count, cols

                print(f"\n🟡 簡稱: {name}")
                for _, row in group.iterrows():
                    count, cols = get_nonnull_info(row)
                    print(f"  ➤ 來源：{row['_來源']}，非空欄位 {count} 個：{', '.join(cols)}")

                print(f"  ✅ 最終選中來源：{selected['_來源']}")
            else:
                final_rows.append(group.iloc[0])

        # 建立最終 DataFrame
        final_df = pd.DataFrame(final_rows).drop(columns=["_non_null_count", "_來源優先", "_來源"])
        final_df = final_df.sort_values(by="音典排序", na_position="last")

        # 寫入資料庫
        final_df.to_sql("dialects", conn, if_exists="replace", index=False)
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_dialects_code ON dialects(簡稱);")

    print(f"✅ SQLite 資料庫 `dialects_query.db` 已建立，dialects 表已更新完成。")


def process_all2sql(tsv_paths, db_path, append=False):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if not append:
        cursor.execute("DROP TABLE IF EXISTS dialects")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dialects (
            簡稱 TEXT,
            漢字 TEXT,
            音節 TEXT,
            聲母 TEXT,
            韻母 TEXT,
            聲調 TEXT,
            註釋 TEXT,
            多音字 TEXT
        )
    ''')
    conn.commit()

    log_lines = []

    def clean_join(series):
        return ", ".join(x.strip() for x in series.dropna().astype(str).unique() if x and x.strip())

    for path in tsv_paths:
        if path == "_":
            continue

        tsv_name = os.path.splitext(os.path.basename(path))[0]
        print(f"\n🔍 正在處理：{tsv_name}")

        try:
            df = extract_all_from_tsv(path)
            print(f"  📄 提取資料表：{len(df)} 行")

            df = df.fillna("")
            df["漢字"] = df["汉字"].astype(str).str.strip()
            df["音節"] = df["音标"].astype(str).str.strip()
            df["聲母"] = df["声母"].astype(str).str.strip()
            df["韻母"] = df["韵母"].astype(str).str.strip()
            df["聲調"] = df["声调"].astype(str).str.strip()
            df["註釋"] = df["註釋"].astype(str).str.strip() if "註釋" in df.columns else ""

            insert_count = 0
            for _, row in df.iterrows():
                char = row["漢字"]
                phonetic = row["音節"]
                cons = row["聲母"]
                vow = row["韻母"]
                tone = row["聲調"]
                note = row["註釋"]

                if not any([cons, vow, tone]):
                    continue

                if not all([cons, vow, tone]):
                    print(f"❗ 缺資料：char={char}, 音節={phonetic}, 聲母='{cons}', 韻母='{vow}', 聲調='{tone}'")

                cursor.execute('''
                    INSERT INTO dialects (簡稱, 漢字, 音節, 聲母, 韻母, 聲調, 註釋, 多音字)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    tsv_name, char, phonetic,
                    cons, vow, tone, note, ""
                ))
                insert_count += 1

            conn.commit()
            log_lines.append(f"{tsv_name} 寫入了 {insert_count} 筆。")
            print(f"✅ {tsv_name} 完成：共寫入 {insert_count} 筆。")

        except Exception as e:
            log_lines.append(f"{tsv_name} 寫入失敗：{e}")
            print(f"❌ 錯誤處理 {tsv_name}：{e}")

    conn.close()
    print(f"\n📦 所有資料已寫入：{db_path}")

    print("\n📊 寫入總結：")
    for line in log_lines:
        print("   " + line)

    log_path = os.path.splitext(db_path)[0] + "_log.txt"
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))
    # print(f"\n📝 已寫入紀錄至：{log_path}")


def process_polyphonic_annotations(db_path: str):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM dialects", conn)

    print(f"🔍 資料庫讀取完成，共 {len(df)} 筆")

    # 一階段：合併同音節註釋（聲母、韻母、聲調一致）
    merged = []
    grouped = df.groupby(["簡稱", "漢字", "音節"])

    for (short_name, char, syllable), group in grouped:
        unique_phonetics = group[["聲母", "韻母", "聲調"]].drop_duplicates()
        if len(unique_phonetics) == 1:
            notes = group["註釋"].dropna().astype(str).str.strip().unique()
            notes = [n for n in notes if n]
            combined_note = ";".join(notes) if notes else ""

            base_row = group.iloc[0].copy()
            if base_row["註釋"] != combined_note:
                print(f"📝 合併註釋：{char} / {syllable} → 「{combined_note}」")
            base_row["註釋"] = combined_note
            merged.append(base_row)
        else:
            print(f"⚠️ 音節相同但聲韻調不同：{char} / {syllable}")
            for _, row in group.iterrows():
                merged.append(row)

    merged_df = pd.DataFrame(merged)
    print(f"✅ 合併後剩餘 {len(merged_df)} 筆")

    # 二階段：標記多音字（音節不同）
    final = []
    grouped2 = merged_df.groupby(["簡稱", "漢字"])

    for (short_name, char), group in grouped2:
        if len(group["音節"].unique()) > 1:
            print(f"🔁 多音字標記：{short_name} / {char}")
            group["多音字"] = "1"
            # for _, row in group.iterrows():
            # print("  ➤", dict(row))
        else:
            group["多音字"] = ""
        final.append(group)

    final_df = pd.concat(final).reset_index(drop=True)

    print(f"💾 清空並重建資料表 dialects，共 {len(final_df)} 筆")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS dialects")
    final_df.to_sql("dialects", conn, index=False)

    conn.commit()
    conn.close()
    print("✅ 多音字處理完成")


def sync_dialects_flags(all_db_path=DIALECTS_DB_PATH,
                        query_db_path=QUERY_DB_PATH,
                        log_path=CHARACTERS_DB_PATH):
    # 讀取 dialects_all.db 中所有唯一簡稱
    conn_all = sqlite3.connect(all_db_path)
    cursor_all = conn_all.cursor()
    cursor_all.execute("SELECT DISTINCT 簡稱 FROM dialects")
    all_tags = set(row[0] for row in cursor_all.fetchall())
    conn_all.close()

    # 讀取 dialects_query.db 中所有簡稱
    conn_query = sqlite3.connect(query_db_path)
    cursor_query = conn_query.cursor()

    # 確保存儲標記欄位存在
    cursor_query.execute("PRAGMA table_info(dialects)")
    columns = [col[1] for col in cursor_query.fetchall()]
    if "存儲標記" not in columns:
        cursor_query.execute("ALTER TABLE dialects ADD COLUMN 存儲標記 INTEGER DEFAULT 0")

    cursor_query.execute("SELECT rowid, 簡稱 FROM dialects")
    query_map = {tag: rowid for rowid, tag in cursor_query.fetchall()}

    matched = []
    unmatched = []

    for tag in sorted(all_tags):
        if tag in query_map:
            rowid = query_map[tag]
            cursor_query.execute("UPDATE dialects SET 存儲標記 = 1 WHERE rowid = ?", (rowid,))
            matched.append(tag)
        else:
            unmatched.append(tag)
            print(f"❗ 無法匹配簡稱：{tag}")

    conn_query.commit()
    conn_query.close()

    # 寫入 log 檔案（前面兩個空行）
    with open(log_path, "a", encoding="utf-8") as f:
        f.write("\n\n")
        for tag in unmatched:
            f.write(f"無法匹配簡稱：{tag}\n")

        # 寫入成功存儲訊息，每 10 個換行
        lines = []
        for i in range(0, len(matched), 10):
            lines.append(", ".join(matched[i:i + 10]))
        success_message = "成功存儲：\n" + "\n".join(lines)
        f.write(success_message + "\n")

    print("✅ 同步完成。已更新存儲標記。")


def process_phonology_excel(
        excel_file=PHO_TABLE_PATH,
        sheet_name="層級",
        db_file=CHARACTERS_DB_PATH,
        log_file="logs/dialects_log.txt"
):
    os.makedirs("data", exist_ok=True)

    # 欄位設置
    columns_needed = ["攝", "呼", "等", "韻", "入", "調", "清濁", "系", "組", "聲", "單字"]
    rename_map = {"單字": "漢字"}
    write_columns = ["攝", "呼", "等", "韻", "入", "調", "清濁", "系", "組", "聲", "漢字"]

    # 讀取 Excel
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet_name, dtype=str)
    except Exception as e:
        print(f"❌ 讀取 Excel 失敗: {e}")
        return

    try:
        df = df[columns_needed].rename(columns=rename_map)
    except KeyError as e:
        print(f"❌ 缺少必要欄位: {e}")
        return

    # 清除漢字為空的行
    df = df[df["漢字"].notna() & (df["漢字"].str.strip() != "")]
    df['num'] = df.index + 2  # Excel 行號

    # 檢查其他欄位是否有缺值（不包含"漢字"與"num"）
    check_cols = [col for col in df.columns if col not in ["漢字", "num"]]
    invalid_rows = df[df[check_cols].isnull().any(axis=1)]

    # 有效列
    df_valid = df.drop(index=invalid_rows.index)

    # 去除完全重複的列（只比較要寫入的列）
    df_unique = df_valid.drop_duplicates(subset=write_columns).copy()

    # 標記「多地位」：同漢字出現多次（但行不同）
    dup_counts = df_unique["漢字"].value_counts()
    df_unique["多地位標記"] = df_unique["漢字"].map(lambda x: "1" if dup_counts.get(x, 0) > 1 else "")

    # 輸出錯誤記錄
    if not invalid_rows.empty:
        invalid_output = invalid_rows[["num", "漢字"] + check_cols]
        print("❗ 發現欄位缺漏如下：")
        print(invalid_output)

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(invalid_output.to_csv(index=False, sep='\t', lineterminator='\n'))

    # 寫入 SQLite
    try:
        conn = sqlite3.connect(db_file)
        df_unique.drop(columns=["num"]).to_sql("characters", conn, if_exists="replace", index=False)
        conn.close()
        print("✅ 成功寫入 SQLite，總筆數：", len(df_unique))
    except Exception as e:
        print(f"❌ SQLite 寫入失敗: {e}")


def write_to_sql(yindian = None, write_chars_db=None):
    #  寫檔案表
    print("开始寫入檔案表")
    build_dialect_database()

    #  寫總數據表
    if yindian:
        tsv_paths_yindian,*_ = get_tsvs(output_dir='data/yindian/')
        tsv_paths_mine, *_ = get_tsvs()
        tsv_paths = tsv_paths_yindian + tsv_paths_mine
    else:
        tsv_paths, *_ = get_tsvs()
    db_path = os.path.join(os.getcwd(), DIALECTS_DB_PATH)
    print("🚀 開始導入資料...")
    process_all2sql(tsv_paths, db_path)
    print("开始处理重复行以及标记多音字")
    process_polyphonic_annotations(DIALECTS_DB_PATH)
    print("开始寫入存儲標記")
    sync_dialects_flags()

    if write_chars_db:
        #  寫漢字地位表
        print("开始寫入漢字地位表")
        process_phonology_excel()
    # print("✅ 測試完成。")


if __name__ == "__main__":
    write_to_sql()
    # build_dialect_database()
