import pandas as pd

from source.Phonology2status import pho2sta
from source.arrange_fromdb import sta2pho
from source.raw2tsv import convert_all_to_tsv
from source.tsv2sql import write_to_sql


def run_phonology_analysis(
        mode: str,
        locations: list,
        regions: list,
        features: list,
        status_inputs: list = None,
        group_inputs: list = None,
        pho_values: list = None
):
    """
    統一介面函數：根據 mode ('s2p' 或 'p2s') 執行 sta2pho 或 pho2sta。

    參數：
        mode: 's2p' = 語音條件 ➝ 統計；'p2s' = 特徵值 ➝ 統計
        locations: 方言點名稱
        features: 語音特徵欄位
        status_inputs: 語音條件字串（如 '知組三'），僅限 's2p'
        group_inputs: 要分組的欄位（如 '組聲'），僅限 'p2s'
        pho_values: 音值條件（如 ['l', 'm', 'an']），僅限 'p2s'

    回傳：
        List[pd.DataFrame]
    """

    if mode == 's2p':
        # if not status_inputs:
        #     raise ValueError("🔴 mode='s2p' 時，請提供 status_inputs。")
        return sta2pho(locations, regions, features, status_inputs)

    elif mode == 'p2s':
        # if not group_inputs :
        #     raise ValueError("🔴 mode='p2s' 時，請提供 group_inputs ")
        return pho2sta(locations, regions, features, group_inputs, pho_values)


    else:
        raise ValueError("🔴 mode 必須為 's2p' 或 'p2s'")


def main():
    # 測試資料
    # status_inputs = [
    #     "知組三 端",
    #     "通开三",
    # ]
    status_inputs = [
        "通开一",
    ]
    regions = [""]
    locations = [ "東莞莞城","雲浮富林"]
    # features = ['聲母', '韻母', '聲調']
    features = ['韻母']
    # group_inputs = ["組聲 攝等 清濁調"]
    pho_value = ["l m an 陰平"]
    group_inputs = ["攝"]
    mode = "p2s"  # or "s2p"

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.width', 0)

    # 字表轉換成tsv
    # convert_all_to_tsv()

    # tsv寫入數據庫
    # write_to_sql()

    # 呼叫分析函數
    results = run_phonology_analysis(
        mode=mode,
        locations=locations,
        regions=regions,
        features=features,
        status_inputs=status_inputs,
        group_inputs=group_inputs,
        pho_values=pho_value
    )


    # 印出結果
    for row in results:
        print(row)


if __name__ == "__main__":
    main()