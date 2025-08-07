import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog

def is_valid_syllable(val):
    """排除空值和只含数字的值"""
    if pd.isna(val):
        return False
    val_str = str(val).strip()
    return val_str != '' and not val_str.isdigit()

# 创建 Tkinter 文件选择对话框
root = tk.Tk()
root.withdraw()

print("请选择要处理的 Excel 文件...")
file_paths = filedialog.askopenfilenames(
    title="选择多个 Excel 文件",
    filetypes=[("Excel 文件", "*.xlsx *.xls")]
)

if not file_paths:
    print("未选择任何文件。")
else:
    print(f"\n共选择了 {len(file_paths)} 个文件。")

    # 选择输出目录
    print("请选择输出文件夹...")
    output_dir = filedialog.askdirectory(title="选择输出文件夹")
    if not output_dir:
        print("未选择输出文件夹，已取消操作。")
    else:
        for idx, file in enumerate(file_paths):
            print(f"\n处理文件 {idx + 1}/{len(file_paths)}: {file}")
            try:
                df = pd.read_excel(file)
                print(f"原始行数: {df.shape[0]}，列数: {df.shape[1]}")

                # 保留并重排指定列
                columns_to_keep = ['fn', 'id', 'ini', 'notes', 'phrase', 'pt', 'syllable']
                df = df[columns_to_keep]
                df = df[['id', 'ini', 'fn', 'pt', 'phrase', 'syllable', 'notes']]

                # # 删除无效 syllable 行
                # before = df.shape[0]
                # df = df[df['syllable'].apply(is_valid_syllable)]
                # after = df.shape[0]
                # print(f"删除无效 syllable 行数: {before - after}")

                # 重命名列
                df = df.rename(columns={
                    'phrase': '单字',
                    'syllable': 'IPA',
                    'notes': '注释'
                })

                # 生成输出文件路径
                base_name = os.path.splitext(os.path.basename(file))[0]
                output_file = os.path.join(output_dir, f"{base_name}_processed.xlsx")

                df.to_excel(output_file, index=False)
                print(f"处理完成，已保存到：{output_file}")

            except Exception as e:
                print(f"处理文件时出错：{file}")
                print(f"错误信息：{e}")
