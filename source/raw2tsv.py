import os
import glob
import re
import tkinter as tk
from tkinter import filedialog
import pandas as pd

from source.convert_jyut import process_yutping_file, build_replace_table
from source.format_convert import process_音典, process_跳跳老鼠, process_縣志
from source.process_tones import extract_tone_maps, convert_tones, tone_jyut2yindian
from source.config import APPEND_PATH

# 處理函數定義
format_handlers = {
    "音典": process_音典,
    "跳跳老鼠": process_跳跳老鼠,
    "縣志": process_縣志

}

# 讀取 Append_files.xlsx.xlsx
dialect_path = APPEND_PATH
df_meta = pd.read_excel(dialect_path)


def get_simplified_level(name, simplified_setting):
    """
    判斷表格使用簡體還是繁體轉換規則
    """
    setting = simplified_setting.get(name)
    if setting == "简":
        print(f"🔍 {name}：標記為簡體，將進行繁化處理。")
        return 2
    else:
        if setting:
            print(f"ℹ️ {name}：已列出但標記為「{setting}」，不進行轉換。")
        else:
            print(f"ℹ️ {name}：未列出，預設為繁體，不轉換。")
        return 1


def process_columns_name(file, col_letters):
    """
    處理 Excel 檔案中的欄位名稱，根據使Dialects_files.xlsx裡面的“字聲韻調註列名”列（例如：A,B,C 或 A,(G),H），
    將其對應的欄位名稱重新命名為標準名稱：
        - "漢字_程序改名"
        - "IPA_程序改名"
        - "注釋_程序改名"

    如果中間的欄位使用括號包起來（例如 A,(G),H），則視為粵拼欄位，並將名稱改為 "粵拼_程序改名"。

    :param file: Excel 檔案路徑
    :param col_letters: 欄位字母設定（以逗號分隔，例如 "A,B,C" 或 "A,(G),H"）
    :return: 無直接回傳，會就地修改 Excel 中的欄位名稱
    """
    print(f"[音典列名] 處理 {file}，使用設定：{col_letters}")
    try:
        df = pd.read_excel(file, sheet_name=None)  # 讀取所有工作表
        for sheet_name, sheet_df in df.items():
            header = sheet_df.columns.tolist()
            print(f"[DEBUG] Sheet「{sheet_name}」原表頭：{header}")

            # 根據括號判斷是否為粵拼列
            raw_letters = [c.strip() for c in re.split(r'[，,]', col_letters)]
            letters = []
            target_names = []

            for i, ltr in enumerate(raw_letters[:3]):
                is_cantonese = ltr.startswith("(") and ltr.endswith(")")
                clean_ltr = ltr.replace("(", "").replace(")", "").strip().upper()

                letters.append(clean_ltr)
                if is_cantonese:
                    target_names.append("粵拼_程序改名")
                elif i == 0:
                    target_names.append("漢字_程序改名")
                elif i == 1:
                    target_names.append("IPA_程序改名")
                elif i == 2:
                    target_names.append("注釋_程序改名")

            if len(letters) < 3:
                print(f"[WARNING] 欄位設定不足三欄：{letters}")
                continue

            # 取出三個指定欄的實際欄位名
            actual_names = []
            for letter in letters[:3]:
                if letter.isalpha() and len(letter) == 1:
                    idx = ord(letter) - ord("A")
                    actual_names.append(header[idx].strip() if 0 <= idx < len(header) else None)
                else:
                    actual_names.append(None)

            # 若已符合目標欄名，略過
            if actual_names == target_names:
                print(f"[INFO] Sheet「{sheet_name}」指定欄位已符合預期命名，略過重命名")
                continue

            # 建立重命名對應
            rename_map = {}
            for i, new_name in enumerate(target_names):
                letter = letters[i]
                if letter.isalpha() and len(letter) == 1:
                    idx = ord(letter) - ord("A")
                    if 0 <= idx < len(header):
                        old_name = header[idx]
                        rename_map[old_name] = new_name
                        print(f"[DEBUG] 欄位重命名：{letter} → 第 {idx + 1} 欄（{old_name} → {new_name}）")
                    else:
                        print(f"[WARNING] 字母 {letter} 超出欄位範圍（共 {len(header)} 欄）")
                else:
                    print(f"[WARNING] 無效的欄位字母：{letter}")

            # 寫入結果
            if rename_map:
                new_df = sheet_df.rename(columns=rename_map)
                with pd.ExcelWriter(file, mode='a', if_sheet_exists='replace', engine='openpyxl') as writer:
                    new_df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"🛠️ {os.path.basename(file)} 中 Sheet「{sheet_name}」已重命名欄位：{rename_map}")
            break  # 只處理第一個符合的 sheet
    except Exception as e:
        print(f"❗讀取或寫入 Excel 時發生錯誤：{e}")


def choose_files():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilenames(filetypes=[
        ("支持格式", "*.tsv *.xlsx *.xls *.docx" "*.doc"),
        ("所有文件", "*.*")
    ])


def match_files_from_excel(meta_df, data_folder):
    """
    根據 meta_df 的「文件名」欄位與 data_folder 中的實際檔案進行匹配。
    嚴格匹配前綴與副檔名。

    返回 dict: { pattern_name_in_excel: full_path_to_file }
    """
    # print(meta_df)
    all_files = glob.glob(os.path.join(data_folder, "*"))
    result = {}
    # ✅ 僅保留「已做」的行，且文件名非空
    filtered_df = meta_df[
        meta_df["是否有人在做"].astype(str).str.strip() == "已做"
    ].copy()
    filtered_df = filtered_df[filtered_df["文件名"].notna()]

    for pattern_name in filtered_df["文件名"]:
        match_prefix = pattern_name.split("*")[0]
        expected_ext = os.path.splitext(pattern_name)[1].lower()
        matched_path = None

        for file in all_files:
            basename = os.path.basename(file)
            actual_ext = os.path.splitext(basename)[1].lower()

            if basename.startswith(match_prefix) and actual_ext == expected_ext:
                matched_path = file
                break

        if matched_path:
            result[pattern_name] = matched_path
            print(f"✅ 匹配成功：{pattern_name} → {os.path.basename(matched_path)}")
        else:
            print(f"⚠️ 未匹配任何文件：{pattern_name}")

    return result


def build_config_map(meta_df):
    return {
        "format_map": dict(zip(meta_df["簡稱"], meta_df["字表格式"])),
        "simplified_setting": dict(zip(meta_df["簡稱"], meta_df["繁簡"])),
        "col_letter_map": dict(zip(meta_df["簡稱"], meta_df.get("字聲韻調註列名", ""))),
        "file_map": dict(zip(meta_df["簡稱"], meta_df["文件名"])),
        "tone_setting": dict(zip(meta_df["簡稱"], meta_df["字表使用調值"])),
        "include_setting": dict(zip(meta_df["簡稱"], meta_df.get("是否有人在做", "否"))),
        "pinyin_setting": dict(zip(meta_df["簡稱"], meta_df.get("拼音", "")))

    }


def process_single_file(file, shortname, config, output_folder):
    """
    處理單個文件
    """
    basename = os.path.basename(file)
    file_format = config["format_map"].get(shortname)
    pinyin_setting = config["pinyin_setting"].get(shortname, "")

    if file_format not in format_handlers:
        print(f"❌ 找不到對應處理函數：「{file_format}」，略過 {shortname}")
        os.makedirs("data", exist_ok=True)
        with open("logs/error.txt", "a", encoding="utf-8") as f:
            f.write(f"❌ [{shortname}] 找不到對應處理函數：「{file_format}」\n")
        return

    # 音典格式 → 處理欄位名
    if file_format == "音典":
        col_letters = config["col_letter_map"].get(shortname)
        if col_letters:
            process_columns_name(file, col_letters)
        else:
            print(f"⚠️ 無對應欄位代碼設定：{shortname}，跳過欄位重命名")
    # 如果設定指定處理粵拼欄位，則進行 IPA 轉換
    if pinyin_setting in ["粵拼", "粤拼"]:
        print(f"🔧 檢測到拼音欄位設定為 {pinyin_setting}，執行 粵拼轉IPA 處理...")
        replace_df = build_replace_table()
        process_yutping_file(file, replace_df, convert_tone=False, debug=True)

    output_path = os.path.join(output_folder, f"{shortname}.tsv")
    level = get_simplified_level(shortname, config["simplified_setting"])

    # ✅ 第一步：先處理格式並輸出 .tsv
    print(f"🚀 處理文件：{basename}，格式：{file_format}")
    func = format_handlers[file_format]
    func(file, level, output_path)

    # ✅ 第二步：處理 tone 替換
    if config["tone_setting"].get(shortname) == "☑":
        print(f"🔁 進行 tone 轉換：{shortname}")
        tone = extract_tone_maps(shortname)
        print("🎯 tone_shu =", tone["shu"])
        print("🎯 tone_ru =", tone["ru"])
        print("🎯 tone_bian =", tone["bian"])

        converted_df = convert_tones(tone, shortname)
        # print(converted_df)
        if not converted_df.empty:
            print("✅ 轉換結果預覽：")
            print(converted_df.head(10))
        else:
            print("⚠️ 無法轉換 tone 或檔案內容為空")

    # ⭐ 粵拼轉 yindian tone（只在 tone_setting 為 ☑ 且 pinyin_setting 是 粵拼）
    if config["tone_setting"].get(shortname) == "☐" and config["pinyin_setting"].get(shortname) in ["粵拼", "粤拼"]:
        print(f"🎼 進行粵拼調號轉換為 Yindian：{shortname}")
        tone_jyut2yindian(shortname)


def convert_all_to_tsv():
    data_folder = "data/raw"
    output_folder = "data/processed"
    os.makedirs(output_folder, exist_ok=True)

    meta_df = pd.read_excel(APPEND_PATH)
    config = build_config_map(meta_df)
    matched_files = match_files_from_excel(meta_df, data_folder)
    # 🔽 一開始就清空錯誤紀錄
    os.makedirs("data", exist_ok=True)
    with open("logs/error.txt", "w", encoding="utf-8") as f:
        f.write("以下是错误信息：\n")

    for shortname, pattern_name in config["file_map"].items():
        # 僅處理「已做」的項目，其餘跳過
        if config["include_setting"].get(shortname) != "已做":
            print(f"⏩ 跳過（不是『已做』）：{shortname}")
            with open("logs/error.txt", "a", encoding="utf-8") as f:
                f.write(f"⏩ [{shortname}] 跳過（不是『已做』）\n")
            continue

        file = matched_files.get(pattern_name)
        if not file:
            print(f"⚠️ 未匹配任何文件：{shortname}")
            with open("logs/error.txt", "a", encoding="utf-8") as f:
                f.write(f"⚠️ [{shortname}] 未匹配任何文件\n")
            continue

        process_single_file(file, shortname, config, output_folder)


if __name__ == "__main__":
    convert_all_to_tsv()
