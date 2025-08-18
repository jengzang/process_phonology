#  此腳本用來運行scripts路徑下諸多不同功能的程序
from scripts.check.checks import check_pro
from scripts.jyut2ipa.replace import jyut2ipa
from scripts.merge.wordsheet_merge import merge_main


def main(TYPE):

    if TYPE == 'CHECK':
        #  檢查字表格式及錯字
        MODE = 'only'
        check_pro(MODE)
    elif TYPE == 'jyut':
        jyut2ipa()
    elif TYPE == 'MERGE':
        merge_main()


if __name__ == '__main__':
    TYPE = 'CHECK'
    main(TYPE)



