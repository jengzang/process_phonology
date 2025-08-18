from make.source.raw2tsv import convert_all_to_tsv
from make.source.tsv2sql import write_to_sql, sync_dialects_flags

"""
目前用来前置处理字表，转成tsv，然后写入数据库。
"""


def main():

    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_colwidth', None)
    # pd.set_option('display.width', 0)

    # 字表轉換成tsv
    # convert_all_to_tsv()

    # tsv寫入數據庫
    write_to_sql(yindian=YIN_DIAN, write_chars_db=WRITE_CHARS_DB, append=APPEND)

    # 存儲標記
    # sync_dialects_flags()


if __name__ == "__main__":
    YIN_DIAN = True
    WRITE_CHARS_DB = False
    APPEND = False
    main()
