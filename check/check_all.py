import tkinter as tk
from tkinter import filedialog

from get_new import extract_all_from_tsv

# 使用者選擇多個 TSV 檔案
root = tk.Tk()
root.withdraw()

tsv_paths = filedialog.askopenfilenames(
    title="選擇多個 TSV 文件",
    filetypes=[("TSV Files", "*.tsv")]
)

# 對每個檔案執行 extract_all_from_tsv
all_results = []

for path in tsv_paths:
    df = extract_all_from_tsv(path)
    all_results.append(df)

# 現在 all_results 是多個 DataFrame 的列表
print(f"共載入 {len(all_results)} 個 TSV 檔案")
