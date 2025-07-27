import os
import re
import sys
import tkinter as tk
from tkinter import filedialog

from source.config import CHARACTERS_DB_PATH
from source.get_new import extract_all_from_files  # 绝对导入
from source.status_arrange_pho import run_status

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # 添加项目根目录到 sys.path

import sqlite3
import pandas as pd


def check_get_chars(df, feature, user_input=None):
    # 如果 test_inputs 為空，從字符數據庫自動推導
    if not user_input:
        # print("ℹ️ inputs 為空，自動推導條件字串...")
        db_path_char = CHARACTERS_DB_PATH
        conn = sqlite3.connect(db_path_char)
        df_char = pd.read_sql_query("SELECT * FROM characters", conn)
        conn.close()

        auto_inputs = []
        auto_features = []

        if feature == "声母":
            unique_vals = sorted(df_char["聲"].dropna().unique())
            auto_inputs.extend([f"{v}聲" for v in unique_vals])
            # auto_features.extend(["声母"] * len(unique_vals))

        elif feature == "韵母":
            unique_vals = sorted(df_char["攝"].dropna().unique())
            auto_inputs.extend([f"{v}攝" for v in unique_vals])
            # auto_features.extend(["韵母"] * len(unique_vals))

        elif feature == "声调":
            clean_vals = sorted(df_char["清濁"].dropna().unique())
            tone_vals = sorted(df_char["調"].dropna().unique())
            for cv in clean_vals:
                for tv in tone_vals:
                    auto_inputs.append(f"{cv}{tv}")
                    # auto_features.append("声调")

        else:
            print(f"⚠️ 未支援的特徵類型：{feature}，略過")

        # 更新 test_inputs 和 features
        user_input = auto_inputs
    # print(user_input)
    summary = run_status(user_input, db_path=CHARACTERS_DB_PATH)
    all_results = []
    for path_input, chars, multi, path_details in summary:
        if chars is False:
            print("🛑 查詢失敗或無法解析")
            continue

        for result in path_details:
            path_str = result["path"]
            path_chars = result["characters"]

            if not path_chars:
                continue

            # print(f"\n🔧 開始分析『{path_str}』的特徵分布 ({feature})...\n")
            simplified_input = ''.join(re.findall(r'\[(.*?)\]', path_str))
            # print(f"字列{path_chars}")
            # print(f"輸入{simplified_input}")
            df_new = check_by_status(path_chars, feature, df, simplified_input)
            if not df_new.empty:
                condition1 = (df_new['字數'] < 2) & (df_new['佔比'] < 0.08)
                condition2 = df_new['佔比'] < 0.03
                filtered_df = df_new[condition1 | condition2]
                all_results.append(filtered_df)
    return all_results

def check_by_status(chars, feature, df, user_input=None):
    """
    根據提供的漢字名單，查詢其在語音特徵（如聲母/韻母/聲調）下的分佈情況。

    功能：
    - 計算每種語音特徵值（如 b, p, m...）的字數、比例（去重後）

    輸出：
    - 每筆統計結果以字典方式輸出，最終轉為 DataFrame
    """

    # 統計結果存放的列表
    results = []
    loc_chars_df = df[df["汉字"].isin(chars)]
    # print(f"   - 匹配輸入漢字筆數：{len(loc_chars_df)} / {len(chars)}")
    total_chars = len(loc_chars_df["汉字"].unique())

    feature_groups = loc_chars_df.groupby(feature)

    for fval, sub_df in feature_groups:
        # 获取每个特征值下的所有汉字，并去重
        all_chars = sub_df["汉字"].tolist()
        unique_chars = list(set(all_chars))
        count = len(unique_chars)

        # 输出每个特征值的统计信息
        results.append({
            "特徵類別": feature,
            "特徵值": user_input,  # 使用 user_input 作为特徵值
            "分組值": fval,  # 这里的分组值直接是 fval（即特征值）
            "字數": count,
            "佔比": round(count / total_chars, 4) if total_chars else 0.0,
            "對應字": unique_chars,
        })

    # print("\n✅ 分析完成！")

    # 返回结果 DataFrame
    return pd.DataFrame(results)


def select_files():
    # 使用 tkinter 打開文件選擇框，允許選擇多個文件
    root = tk.Tk()
    root.withdraw()  # 隱藏主窗口
    file_paths = filedialog.askopenfilenames(title="選擇文件", filetypes=(
        ("Excel 文件", "*.xls;*.xlsx"), ("TSV 文件", "*.tsv"), ("所有文件", "*.*")))

    if not file_paths:
        print("未選擇任何文件")
        return

    # 處理每個選中的文件
    for file_path in file_paths:
        # 調用提取處理函數並將結果打印在命令行
        df = extract_all_from_files(file_path)
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
        all_unique_chars_list = list(all_unique_chars)
        # 打印结果
        print(all_unique_chars_list)
        print(len(all_unique_chars_list))
        # 添加 "簡稱" 列，内容是去除后缀的文件名
        # df['簡稱'] = os.path.splitext(os.path.basename(file_path))[0]
        # if '汉字' in df.columns:
        #     df.rename(columns={'汉字': '漢字'}, inplace=True)
        # analyze_characters_from_db()
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_colwidth', None)
        pd.set_option('display.width', 0)
        # print(f"處理結果 - {file_path}：")



if __name__ == "__main__":
    select_files()
