# 讀取層級工作表
import pandas as pd

from common.config import PHO_TABLE_PATH
from common.s2t import s2t_pro

DEBUG = True  # 👉 這裡打開/關閉調試輸出

# 讀取層級工作表
df = pd.read_excel(PHO_TABLE_PATH, sheet_name="層級")
original_chars = df["單字"].astype(str).tolist()
original_char_set = set(original_chars)

new_rows = []
seen_pairs = set()  # 為防止重複加相同行

for i, 原字 in enumerate(original_chars):
    clean_str, mapping = s2t_pro(原字, level=1)

    if DEBUG:
        print(f"🔍 原字: {原字} → clean_str: {clean_str}")
        print(f"    Mapping: {mapping}")

    for _, 候選列表 in mapping:
        for 新字 in 候選列表:
            if 新字 not in original_char_set:
                key = (原字, 新字)
                if key not in seen_pairs:
                    seen_pairs.add(key)

                    new_row = df.iloc[i].copy()
                    new_row["單字"] = 新字
                    new_rows.append(new_row)

                    if DEBUG:
                        print(f"➕ 補充：{原字} → {新字}（行複製自 index {i}）")

if new_rows:
    df_new = pd.DataFrame(new_rows)
    output_path = "補充單字輸出.xlsx"
    df_new.to_excel(output_path, index=False)
    print(f"\n✅ 補充行已輸出至：{output_path}")
    print(f"📦 共新增 {len(df_new)} 行")
else:
    print("✅ 無需補充，所有新字皆已存在原始資料中。")