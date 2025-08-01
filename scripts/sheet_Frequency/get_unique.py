"""
获取所有不同的声韵，主函数没调用这个，该脚本是测试用
"""
import os
import pandas as pd
from collections import defaultdict
from gets import get_consonants_from_tsv, get_vowels_from_tsv
from matching_from_xlsx import choose_tsv_files

EXCEL_PATH = "unique_consonants.xlsx"
CATEGORY_COLUMN = "声韵"
SOURCE_COLUMN = "來源文件"


def process(tsv_paths: list, excel_output_path: str, category_column: str = "声韵"):
    consonant_sources = defaultdict(set)

    print(f"🔍 共選擇 {len(tsv_paths)} 個 TSV 文件進行處理。")
    for idx, path in enumerate(tsv_paths, 1):
        print(f"\n📄 [{idx}] 處理文件：{path}")
        try:
            ##################################################
            df = get_vowels_from_tsv(path, char_list="all")
            ##################################################
            if df.empty:
                print("⚠️ 提取結果為空，略過該文件。")
                continue

            filename = os.path.splitext(os.path.basename(path))[0]  # 去除 .tsv
            consonants = df[category_column].dropna().tolist()
            print(f"✅ 提取 {len(consonants)} 條聲韻記錄。")

            for c in consonants:
                consonant_sources[c].add(filename)
        except Exception as e:
            print(f"❌ 解析文件失敗：{e}")

    print(f"\n📊 去重後的聲韻總數：{len(consonant_sources)}")

    # 整理輸出 DataFrame
    output_data = [
        (consonant, ",".join(sorted(files)))
        for consonant, files in sorted(consonant_sources.items())
    ]
    output_df = pd.DataFrame(output_data, columns=[category_column, SOURCE_COLUMN])
    output_df.to_excel(excel_output_path, index=False)
    print(f"📁 已成功將聲韻列表輸出至：{excel_output_path}")


if __name__ == "__main__":
    tsv_files, *_ = choose_tsv_files("嶺南 嶺西 廣中 嶺東 閩 湘赣 浙南 兩浙")  # 嶺南 嶺西 廣中 嶺東 閩 湘赣 浙南 兩浙
    if tsv_files:
        process(tsv_files, EXCEL_PATH, CATEGORY_COLUMN)
    else:
        print("⚠️ 未選擇任何TSV文件，程序結束。")
