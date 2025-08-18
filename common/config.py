import os

# ============ 路徑 =================
# 計算專案根目錄路徑
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

HTML_PATH = os.path.join(BASE_DIR, "index.html")
JS_PATH = os.path.join(BASE_DIR, "app", "js")
CSS_PATH = os.path.join(BASE_DIR, "app", "css")

# database路徑依賴
QUERY_DB_PATH = os.path.join(BASE_DIR, "data", "dialects_query.db")
DIALECTS_DB_PATH = os.path.join(BASE_DIR, "data", "dialects_all.db")
CHARACTERS_DB_PATH = os.path.join(BASE_DIR, "data", "characters.db")
SUPPLE_DB_PATH = os.path.join(BASE_DIR, "data", "supplements.db")
# QUERY_DB_PATH = "C:/Users/joengzaang/PycharmProjects/process_phonology/data/dialects_query.db"
# DIALECTS_DB_PATH = "C:/Users/joengzaang/PycharmProjects/process_phonology/data/dialects_all.db"
# CHARACTERS_DB_PATH = "C:/Users/joengzaang/PycharmProjects/process_phonology/data/characters.db"

# 字表寫入SQL路徑依賴
APPEND_PATH = os.path.join(BASE_DIR, "make", "data", "dependency", "jengzang補充.xlsx")
HAN_PATH = os.path.join(BASE_DIR,  "make", "data", "dependency", "漢字音典字表檔案（長期更新）.xlsx")
HAN_CSV_PATH = os.path.join(BASE_DIR,  "make", "data", "dependency", "漢字音典字表檔案（長期更新）-檔案.csv")  # 暫未使用
PHO_TABLE_PATH = os.path.join(BASE_DIR,  "make", "data", "dependency", "聲韻.xlsx")
RAW_DATA_DIR = os.path.join(BASE_DIR,  "make", "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR,  "make", "data", "processed")
YINDIAN_DATA_DIR = os.path.join(BASE_DIR,  "make", "data", "yindian")
# APPEND_PATH = "C:/Users/joengzaang/PycharmProjects/process_phonology/data/dependency/Append_files.xlsx"
# HAN_PATH = "C:/Users/joengzaang/PycharmProjects/process_phonology/data/dependency/漢字音典字表檔案（長期更新）.xlsx"
# PHO_TABLE_PATH = "C:/Users/joengzaang/PycharmProjects/process_phonology/data/dependency/聲韻.xlsx"

# 通用路徑依賴
ZHENGZI_PATH = os.path.join(BASE_DIR, "data", "dependency", "正字.tsv")
MULCODECHAR_PATH = os.path.join(BASE_DIR, "data", "dependency", "mulcodechar.dt")
# ZHENGZI_PATH = "C:/Users/joengzaang/PycharmProjects/process_phonology/data/dependency/正字.tsv"
# MULCODECHAR_PATH = "C:/Users/joengzaang/PycharmProjects/process_phonology/data/dependency/mulcodechar.dt"

# api_logs路徑依賴
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)  # ✅ 主动创建 logs 目录
KEYWORD_LOG_FILE = os.path.join(log_dir, "api_keywords_log.txt")
SUMMARY_FILE = os.path.join(log_dir, "api_keywords_summary.txt")
API_USAGE_FILE = os.path.join(log_dir, "api_usage_stats.txt")
API_DETAILED_FILE = os.path.join(log_dir, "api_detailed_stats.txt")
API_DETAILED_JSON = os.path.join(log_dir, "api_detailed_stats.json")

# 字表處理路徑依賴
MISSING_DATA_LOG = os.path.join(BASE_DIR, "logs", "缺資料.txt")
WRITE_INFO_LOG = os.path.join(BASE_DIR, "logs", "write.txt")
WRITE_ERROR_LOG = os.path.join(BASE_DIR, "logs", "write_error.txt")
# =============== 配置 =======================
# banner配置
APP_NAME = "Dialect Compare Tool — FastAPI Backend"
AUTHOR = "不羈 (JengZang)"
VERSION = "1.0.1"
DATE_STR = "2025-08-18"

# 運行方式
_RUN_TYPE = 'PACK'

