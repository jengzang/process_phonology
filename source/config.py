# APPEND_PATH = "C:/Users/joengzaang/PycharmProjects/process_phonology/data/dependency/Append_files.xlsx"
# HAN_PATH = "C:/Users/joengzaang/PycharmProjects/process_phonology/data/dependency/漢字音典字表檔案（長期更新）.xlsx"
# PHO_TABLE_PATH = "C:/Users/joengzaang/PycharmProjects/process_phonology/data/dependency/聲韻.xlsx"
# QUERY_DB_PATH = "C:/Users/joengzaang/PycharmProjects/process_phonology/data/dialects_query.db"
# DIALECTS_DB_PATH = "C:/Users/joengzaang/PycharmProjects/process_phonology/data/dialects_all.db"
# CHARACTERS_DB_PATH = "C:/Users/joengzaang/PycharmProjects/process_phonology/data/characters.db"
# ZHENGZI_PATH = "C:/Users/joengzaang/PycharmProjects/process_phonology/data/dependency/正字.tsv"
# MULCODECHAR_PATH = "C:/Users/joengzaang/PycharmProjects/process_phonology/data/dependency/mulcodechar.dt"

import os

# 計算專案根目錄路徑
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# 不改變變數名稱，只改值的來源
APPEND_PATH = os.path.join(BASE_DIR, "data", "dependency", "Append_files.xlsx")
HAN_PATH = os.path.join(BASE_DIR, "data", "dependency", "漢字音典字表檔案（長期更新）.xlsx")
PHO_TABLE_PATH = os.path.join(BASE_DIR, "data", "dependency", "聲韻.xlsx")
QUERY_DB_PATH = os.path.join(BASE_DIR, "data", "dialects_query.db")
DIALECTS_DB_PATH = os.path.join(BASE_DIR, "data", "dialects_all.db")
CHARACTERS_DB_PATH = os.path.join(BASE_DIR, "data", "characters.db")
SUPPLE_DB_PATH = os.path.join(BASE_DIR, "data", "supplements.db")
ZHENGZI_PATH = os.path.join(BASE_DIR, "data", "dependency", "正字.tsv")
MULCODECHAR_PATH = os.path.join(BASE_DIR, "data", "dependency", "mulcodechar.dt")

