import pandas as pd
import os
import re
from collections import Counter  # 用于统计频次

# 假设文件名是 "語保字音表.xlsx"，并且该文件在当前路径下
file_path = '語保字音表.xlsx'

# 对应词语表
word_list = {
    "全清-平": ["东", "该", "灯", "风"],
    "次清-平": ["通", "开", "天", "春"],
    "次浊-平": ["门", "龙", "牛", "油"],
    "全浊-平": ["铜", "皮", "糖", "红"],
    "全清-上": ["懂", "古", "鬼", "九"],
    "次清-上": ["统", "苦", "讨", "草"],
    "次浊-上": ["买", "老", "五", "有"],
    "全浊-上": ["动", "罪", "近", "后"],
    "全清-去": ["冻", "怪", "半", "四"],
    "次清-去": ["痛", "快", "寸", "去"],
    "次浊-去": ["卖", "路", "硬", "乱"],
    "全浊-去": ["洞", "地", "饭", "树"],
    "全清-入": ["谷", "百", "搭", "节", "急"],
    "次清-入": ["哭", "拍", "塔", "切", "刻"],
    "次浊-入": ["六", "麦", "叶", "月"],
    "全浊-入": ["毒", "白", "盒", "罚"]
}

# 读取 Excel 文件中的所有工作表
xls = pd.ExcelFile(file_path)

# 遍历所有工作表
for sheet_name in xls.sheet_names:
    print(f"开始处理工作表：{sheet_name}")  # 输出当前正在处理的工作表名
    # 读取每个工作表的数据
    df = pd.read_excel(xls, sheet_name=sheet_name)

    # 将 "方言点" 列设置为索引
    df.set_index('方言点', inplace=True)

    # 创建一个新的 DataFrame 用于存储结果
    result_df = pd.DataFrame()

    # 1. 分组：根据“方言点”进行分组，逐个处理每个方言点的组
    for dialect_point, group in df.groupby(df.index):
        print(f"正在处理方言点：{dialect_point}")  # 输出当前方言点的名称

        # 2. 为每个音调-声母组合填充声调值
        for tone_key, words in word_list.items():
            # 3. 查找这些字对应的声调(d)
            tone_values = []

            # 遍历词语列表，查找对应的字
            for word in words:
                # 查找所有匹配的行
                matching_rows = group[group['word'] == word]

                # 获取对应的声调列(d)
                for _, row in matching_rows.iterrows():
                    tone_values.append(row['d'])

            # 如果有找到声调数据，统计出现频率并填入频次最高的声调
            if tone_values:
                most_common_tone = Counter(tone_values).most_common(1)[0][0]  # 获取出现频次最高的声调
                result_df.loc[dialect_point, tone_key] = most_common_tone  # 填充对应的列

        # 2. 替换 "s" 列中的 "h" 部分，保留 "p" 并替换 "h" 为 "ʰ"
        # 仅在方言点内进行替换操作
        group['s'] = group['s'].apply(lambda x: x.replace('h', 'ʰ') if isinstance(x, str) and x != 'h' else x)

        # 3. 创建 "ipa" 列，合并 "s", "y", "d"
        group['ipa'] = group['s'] + group['y'] + group['d'].astype(str)

        # 4. 修改列名
        group = group.rename(columns={
            'word': '单字',
            's': '声母',
            'y': '韵母',
            'd': '声调',
            'note': '注释'
        })

        # 5. 创建第一个工作表的内容（词条数据）
        group_first_sheet = group[['单字', '声母', '韵母', '声调', '注释', 'ipa']]  # 包含新的 ipa 列

        # 6. 创建第二个工作表（方言点信息）
        dialect_info = group[
            ['sheng', 'shi', 'xian', 'cun', 'jiedao', 'jing', 'wei', 'yuyan1', 'yuyan2', 'yuyan3']].drop_duplicates()

        # 7. 添加音调-声母组合列到第二个工作表
        # 这些列是 `全清-平`, `次清-平`, ... 由 `result_df` 填充的
        for tone_key in word_list.keys():
            dialect_info[tone_key] = result_df.loc[dialect_point, tone_key] if dialect_point in result_df.index else ""

        # 8. 获取 "shi", "xian", "yuyan1" 的第一个非空值，空则输出 "/"
        shi = group['shi'].dropna().iloc[0] if not group['shi'].isnull().all() else '空'
        xian = group['xian'].dropna().iloc[0] if not group['xian'].isnull().all() else '空'
        yuyan1 = group['yuyan1'].dropna().iloc[0] if not group['yuyan1'].isnull().all() else '空'

        # 9. 生成文件名，格式为 f{shi}-{xian}({yuyan1}).xlsx
        output_filename = f"{shi}-{xian}({yuyan1}).xlsx"
        output_path = os.path.join(os.getcwd(), output_filename)

        print(f"生成文件名：{output_filename}")  # 输出生成的文件名

        # 10. 保存每个方言点的数据为独立的 Excel 文件
        with pd.ExcelWriter(output_path) as writer:
            # 第一张工作表保存原始数据
            group_first_sheet.to_excel(writer, sheet_name='字表')

            # 第二张工作表保存音调-声母组合列
            dialect_info.to_excel(writer, sheet_name='方言点信息')

        print(f"已保存：{output_filename}")  # 输出保存的文件名

print("所有文件处理完成！")
