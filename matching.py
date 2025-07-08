import os
from tkinter import filedialog
import tkinter as tk
import pandas as pd
import opencc

custom_variant_dict = {
    "淸": "清",
    "鄕": "鄉",
    "鐵": "鉄",
    "髙": "高",
    "郞": "郎",
    "屛": "屏",
    "靑": "青",
    "尙": "尚",
    "郉": "邢",
    "楡": "榆",
    "峯": "峰"
    # 如需可再擴充
}


def choose_tsv_files(partition_name: str):
    # === 选择文件阶段 ===
    root = tk.Tk()
    root.withdraw()

    file_paths = filedialog.askopenfilenames(
        title="選擇 TSV 文件（可多選）",
        filetypes=[("TSV files", "*.tsv")]
    )

    if not file_paths:
        print("未選擇任何檔案，程式結束。")
        return

    # 文件名 => 原路径映射
    name_to_path = {
        os.path.splitext(os.path.basename(p))[0]: p
        for p in file_paths
    }

    original_locations = [os.path.splitext(os.path.basename(path))[0] for path in file_paths]

    print(f"[調試] 選擇的原始地點：{original_locations}")

    abbreviation_path = r"C:\\Users\\joengzaang\\myfiles\\杂文件\\声韵处理\\漢字音典字表檔案（長期更新）.csv"
    abbreviation_df = pd.read_csv(abbreviation_path)
    print(f"[調試] 載入的簡稱數量：{len(abbreviation_df)}")

    # === 重複檢查 ===
    duplicated_abbr = abbreviation_df[abbreviation_df.duplicated(subset=['簡稱'], keep=False)]
    if not duplicated_abbr.empty:
        filtered = duplicated_abbr[duplicated_abbr['是否有人在做'] != '否']
        if filtered.empty:
            print("所有重複簡稱都標記為'否'，自動忽略。")
        else:
            print("[警告] 以下簡稱有重複，且'是否有人在做'不為'否'：")
            print(filtered[['簡稱']])
            proceed = input("是否繼續執行？(y/n)：")
            if proceed.lower() != 'y':
                raise SystemExit("中止執行，請處理簡稱重複問題後再試。")
        abbreviation_df = abbreviation_df[
            ~((abbreviation_df['簡稱'].isin(duplicated_abbr['簡稱'])) & (abbreviation_df['是否有人在做'] == '否'))]

    abbr_partition_df = abbreviation_df.dropna(subset=["簡稱", "音典分區"])
    sort_order_abbr = abbr_partition_df["簡稱"].tolist()
    partition_raw = abbr_partition_df["音典分區"].tolist()
    partition_map = {
        name: (region.split('-')[0] if '-' in region else region)
        for name, region in zip(sort_order_abbr, partition_raw)
    }

    converter_s2t = opencc.OpenCC('s2t')
    converter_t2s = opencc.OpenCC('t2s')
    converter_variant = opencc.OpenCC('tw2sp.json')

    def apply_custom_variant(text):
        for old, new in custom_variant_dict.items():
            text = text.replace(old, new)
        return text

    matched_locations = []
    matched_set = set()
    unmatched_locations_step1 = []
    # 解析篩選條件
    partition_filter_set = None
    if partition_name.strip() != "全部":
        selected_parts = partition_name.strip().split()
        partition_filter_set = set(selected_parts)
        print(f"[調試] 篩選分區：{partition_filter_set}")
    print("=== 匹配調訊輸出 ===")

    for loc in original_locations:
        if loc in sort_order_abbr:
            matched_locations.append(loc)
            matched_set.add(loc)
            print(f"Step1 匹配：{loc} -> 簡簿")
        else:
            unmatched_locations_step1.append(loc)

    sort_order_abbr_trad = [converter_s2t.convert(x) for x in sort_order_abbr]
    unmatched_locations_step2 = []
    for loc in unmatched_locations_step1:
        if loc in sort_order_abbr_trad:
            matched_locations.append(loc)
            matched_set.add(loc)
            print(f"Step2 匹配：{loc} -> 簡簿(簡轉繁)")
        else:
            unmatched_locations_step2.append(loc)

    sort_order_abbr_simp = [converter_t2s.convert(x) for x in sort_order_abbr]
    unmatched_locations_step3 = []
    for loc in unmatched_locations_step2:
        loc_simp = converter_t2s.convert(loc)
        if loc_simp in sort_order_abbr_simp:
            matched_locations.append(loc)
            matched_set.add(loc)
            print(f"Step3 匹配：{loc}(轉簡體) -> 簡簿(轉簡體)")
        else:
            unmatched_locations_step3.append(loc)

    abbr_variant_set = set(converter_variant.convert(x) for x in sort_order_abbr)
    unmatched_locations_step4 = []
    for loc in unmatched_locations_step3:
        loc_var = converter_variant.convert(loc)
        if loc_var in abbr_variant_set:
            matched_locations.append(loc)
            matched_set.add(loc)
            print(f"Step4 匹配：{loc}(異體簡化為 {loc_var}) -> 簡簿(異體簡化)")
        else:
            unmatched_locations_step4.append(loc)

    abbr_custom_set = set(apply_custom_variant(x) for x in sort_order_abbr)
    unmatched_locations = []
    for loc in unmatched_locations_step4:
        loc_custom = apply_custom_variant(loc)
        if loc_custom in abbr_custom_set:
            matched_locations.append(loc)
            matched_set.add(loc)
            print(f"Step5 匹配：{loc}(自定義轉為 {loc_custom}) -> 簡簿(自定義)")
        else:
            unmatched_locations.append(loc)
            print(f"未匹配：{loc}(自定義轉為 {loc_custom})")

    # sorted_matched = [abbr for abbr in sort_order_abbr if abbr in matched_set]
    sorted_matched = [
        abbr for abbr in sort_order_abbr
        if abbr in matched_set and (
                partition_filter_set is None or partition_map.get(abbr, '') in partition_filter_set
        )
    ]

    locations = []
    partitions = []
    sorted_paths = []
    previous_partition = None
    for loc in sorted_matched:
        current_partition = partition_map.get(loc, '')
        if previous_partition is not None and current_partition != previous_partition:
            locations.append("_")
            sorted_paths.append("_")
            partitions.append("")
        locations.append(loc)
        sorted_paths.append(name_to_path[loc])
        partitions.append(current_partition)
        previous_partition = current_partition

    # if unmatched_locations:
        # locations.append("__")
        # partitions.append("")
        # locations.extend(unmatched_locations)
        # partitions.extend([''] * len(unmatched_locations))

    print("\n=== 最終排序結果 ===")
    for loc, part in zip(locations, partitions):
        print(f"{loc}\t{part}")

    print("\n=== 匹配成功 ===")
    print(matched_locations)

    print("\n=== 未匹配 ===")
    print(unmatched_locations)

    return sorted_paths, locations, partitions


def process_and_sort_locations(original_locations):
    abbreviation_path = r"C:\\Users\\joengzaang\\myfiles\\杂文件\\声韵处理\\漢字音典字表檔案（長期更新）.csv"
    abbreviation_df = pd.read_csv(abbreviation_path)

    # 檢查簡稱是否有重複
    duplicated_abbr = abbreviation_df[abbreviation_df.duplicated(subset=['簡稱'], keep=False)]
    if not duplicated_abbr.empty:
        filtered = duplicated_abbr[duplicated_abbr['是否有人在做'] != '否']
        if filtered.empty:
            print("所有重複簡稱都標記為'否'，自動忽略。")
        else:
            print("[警告] 以下簡稱有重複，且'是否有人在做'不為'否'：")
            print(filtered[['簡稱']])
            proceed = input("是否繼續執行？(y/n)：")
            if proceed.lower() != 'y':
                raise SystemExit("中止執行，請處理簡稱重複問題後再試。")
        abbreviation_df = abbreviation_df[
            ~((abbreviation_df['簡稱'].isin(duplicated_abbr['簡稱'])) & (abbreviation_df['是否有人在做'] == '否'))]

    abbr_partition_df = abbreviation_df.dropna(subset=["簡稱", "音典分區"])

    sort_order_abbr = abbr_partition_df["簡稱"].tolist()
    partition_raw = abbr_partition_df["音典分區"].tolist()
    partition_map = {
        name: (region.split('-')[0] if '-' in region else region)
        for name, region in zip(sort_order_abbr, partition_raw)
    }

    converter_s2t = opencc.OpenCC('s2t')
    converter_t2s = opencc.OpenCC('t2s')
    converter_variant = opencc.OpenCC('tw2sp.json')

    def apply_custom_variant(text):
        for old, new in custom_variant_dict.items():
            text = text.replace(old, new)
        return text

    matched_locations = []
    matched_set = set()
    unmatched_locations_step1 = []
    print("=== 匹配調訊輸出 ===")

    for loc in original_locations:
        if loc in sort_order_abbr:
            matched_locations.append(loc)
            matched_set.add(loc)
            print(f"Step1 匹配：{loc} -> 簡簿")
        else:
            unmatched_locations_step1.append(loc)

    sort_order_abbr_trad = [converter_s2t.convert(x) for x in sort_order_abbr]
    unmatched_locations_step2 = []
    for loc in unmatched_locations_step1:
        if loc in sort_order_abbr_trad:
            matched_locations.append(loc)
            matched_set.add(loc)
            print(f"Step2 匹配：{loc} -> 簡簿(簡轉繁)")
        else:
            unmatched_locations_step2.append(loc)

    sort_order_abbr_simp = [converter_t2s.convert(x) for x in sort_order_abbr]
    unmatched_locations_step3 = []
    for loc in unmatched_locations_step2:
        loc_simp = converter_t2s.convert(loc)
        if loc_simp in sort_order_abbr_simp:
            matched_locations.append(loc)
            matched_set.add(loc)
            print(f"Step3 匹配：{loc}(轉簡體) -> 簡簿(轉簡體)")
        else:
            unmatched_locations_step3.append(loc)

    abbr_variant_set = set(converter_variant.convert(x) for x in sort_order_abbr)
    unmatched_locations_step4 = []
    for loc in unmatched_locations_step3:
        loc_var = converter_variant.convert(loc)
        if loc_var in abbr_variant_set:
            matched_locations.append(loc)
            matched_set.add(loc)
            print(f"Step4 匹配：{loc}(異體簡化為 {loc_var}) -> 簡簿(異體簡化)")
        else:
            unmatched_locations_step4.append(loc)

    abbr_custom_set = set(apply_custom_variant(x) for x in sort_order_abbr)
    unmatched_locations = []
    for loc in unmatched_locations_step4:
        loc_custom = apply_custom_variant(loc)
        if loc_custom in abbr_custom_set:
            matched_locations.append(loc)
            matched_set.add(loc)
            print(f"Step5 匹配：{loc}(自定義轉為 {loc_custom}) -> 簡簿(自定義)")
        else:
            unmatched_locations.append(loc)
            print(f"未匹配：{loc}(自定義轉為 {loc_custom})")

    sorted_matched = [abbr for abbr in sort_order_abbr if abbr in matched_set]

    locations = []
    partitions = []
    previous_partition = None
    for loc in sorted_matched:
        current_partition = partition_map.get(loc, '')
        if previous_partition is not None and current_partition != previous_partition:
            locations.append("_")
            partitions.append("")
        locations.append(loc)
        partitions.append(current_partition)
        previous_partition = current_partition

    if unmatched_locations:
        locations.append("__")
        partitions.append("")
        locations.extend(unmatched_locations)
        partitions.extend([''] * len(unmatched_locations))

    return locations, partitions, matched_locations, unmatched_locations, partition_map


# if __name__ == "__main__":
#     paths = choose_tsv_files("嶺南 嶺東")
#     print(paths)
