from source.raw2tsv import convert_all_to_tsv
from source.tsv2sql import write_to_sql, sync_dialects_flags, build_dialect_database, process_phonology_excel

"""
目前用来前置处理字表，转成tsv，然后写入数据库。
"""


import argparse

# === 主執行函式 ===
def main(args):
    # 1️⃣ 字表轉換
    if 'convert' in args.type:
        convert_all_to_tsv()

    # 2️⃣ 寫入資料庫（admin 或 user）
    if not args.type or 'needchars' in args.type:  # 👈 空 or 有 chars 才寫
        if args.user == 'admin':
            write_to_sql(
                yindian=True,
                write_chars_db='needchars' in args.type,
                append='append' in args.type
            )
        elif args.user == 'user':
            write_to_sql(
                yindian='only',
                write_chars_db='needchars' in args.type,
                append='append' in args.type
            )

    # 3️⃣ 建立 dialect 資料表
    if 'query' in args.type:
        build_dialect_database()

    # 4️⃣ 同步方言標記
    if 'sync' in args.type:
        sync_dialects_flags()

    # 5️⃣ 寫入中古地位表
    if 'phonology' in args.type:
        process_phonology_excel()

# === 命令列參數設定 ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="📘 字表預處理工具，支持各種字表格式轉換、數據庫寫入。"
    )

    # 使用者資料庫類型（預設為 admin）
    parser.add_argument(
        '-u', '--user',
        choices=['admin', 'user'],
        default='admin',
        help="👤 指定要寫入的資料庫類型：admin（預設）或 user"
    )

    # 要執行的處理功能（可多選）
    parser.add_argument(
        '-t', '--type',
        nargs='*',
        choices=['convert', 'chars', 'query', 'sync', 'needchars', 'append'],
        default=[],
        help=(
            "⚙️ 要執行的處理功能（可多選）：\n"
            "  convert      → 字表轉TSV\n"
            "  needchars     → 需要寫入中古音數據庫\n"
            "  query        → 寫入方言查詢數據庫\n"
            "  sync         → 儲存方言標記\n"
            "  chars    → 寫入中古地位表\n"
            "  append       → 寫入方式為添加\n"
        )
    )

    args = parser.parse_args()
    main(args)
