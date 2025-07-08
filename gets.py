import math

import pandas as pd
import re

# 定义元音的正则表达式（支持多个元音）
vowel_pattern = r"[iyɨʉɯuɪʏɿʅʅɭıɪſɩɷʮɥʯʊeɘɵəɤoɛεɝɚᴇœɜɞʌɔæaɶɑɒᴀɐãẽĩỹõúαᵘᶷᶤᶶᵚʸᶦᵊⁱ◌∅ø]"


def get_vowels_from_tsv(tsv_file_path: str, char_list: list) -> pd.DataFrame:
    """
    从TSV文件中提取与字列表匹配的所有汉字以及对应的韵母。

    tsv_file_path: TSV文件路径
    char_list: 要查找的汉字列表

    返回: 包含匹配的汉字、音标和韵母的DataFrame
    """
    # 读取TSV文件
    tsv_df = pd.read_csv(tsv_file_path, sep="\t")

    if '#漢字' not in tsv_df.columns:
        print("错误：找不到 '#漢字' 列，请检查文件结构！")
        return pd.DataFrame()  # 返回空的 DataFrame，避免后续错误

    # 如果 char_list 为 'all'，获取所有汉字并去重，忽略 "□" 和 "□ □"
    if char_list == "all":
        char_list = tsv_df['#漢字'].drop_duplicates().tolist()
        char_list = [char for char in char_list if char not in ["□", "□"]]  # 排除 "□" 和 "□ □"
    else:
        char_list = list(dict.fromkeys(char_list))  # 保持顺序去重

    # 存储匹配结果
    matched_results = []

    # 遍历字列表
    for char in char_list:
        # 查找对应汉字的音标
        matched_rows = tsv_df[tsv_df['#漢字'] == char]

        if not matched_rows.empty:
            # 对于每个匹配的汉字，遍历所有音标
            for index, row in matched_rows.iterrows():
                phonetic = row['音標']
                all_rhymes = []

                if not phonetic or (isinstance(phonetic, float) and math.isnan(phonetic)):
                    continue  # 跳過空值或 NaN
                # 如果是字符串且开头是数字，跳过（新增）
                if isinstance(phonetic, str) and phonetic and phonetic[0].isdigit():
                    continue

                # 提取音标中的韵母
                if phonetic.startswith("∅"):
                    phonetic = phonetic[1:]
                # 只有當 phonetic 不含 j/ʲ，或它們出現在第 0 位，才進行韻母提取
                if ('j' not in phonetic[1:] and 'ʲ' not in phonetic[1:]):
                    vowel_found = False
                    for phonetic_char in phonetic:
                        if re.match(vowel_pattern, phonetic_char) and not vowel_found:
                            vowel_found = True
                            all_rhymes.append(phonetic_char)  # 添加第一个元音
                        elif vowel_found and (phonetic_char.isdigit() or phonetic_char.isspace()):
                            break  # 遇到数字或空格时停止
                        elif vowel_found and re.match(vowel_pattern, phonetic_char):
                            all_rhymes.append(phonetic_char)  # 继续添加后续的元音
                        elif vowel_found and not re.match(vowel_pattern, phonetic_char):
                            all_rhymes.append(phonetic_char)  # 遇到辅音继续添加
                    # 鼻化韻：
                    if not vowel_found and any(c in phonetic for c in "mnŋȵƞʋvʒ"):
                        all_rhymes += list(
                            re.match(r".*?([mnŋȵƞʋvʒ].*?)(?=\d|\s|$)", phonetic).group(1)
                        ) if re.search(r"[mnŋȵƞʋvʒ]", phonetic) else []

                    rhyme = ''.join(all_rhymes)
                    # 筛除“声韵”中的汉字和数字
                    rhyme = ''.join(c for c in rhyme if not (c.isdigit() or re.match(r'[\u4e00-\u9fff]', c)))
                    matched_results.append({'汉字': char, '音标': phonetic, '声韵': rhyme})
                else:
                    # j 或 ʲ 出現在中間
                    match = re.search(rf"[{vowel_pattern.strip('()')}jʲ][^\d\s]*", phonetic)
                    rhyme = match.group(0) if match else ''
                    # 筛除“声韵”中的汉字和数字
                    rhyme = ''.join(c for c in rhyme if not (c.isdigit() or re.match(r'[\u4e00-\u9fff]', c)))
                    matched_results.append({'汉字': char, '音标': phonetic, '声韵': rhyme})

    # 转换为DataFrame
    result_df = pd.DataFrame(matched_results)

    # 拆分包含 "/" 的声韵为两个记录
    expanded_results = []
    for row in matched_results:
        consonant = row['声韵']
        if '/' in consonant and consonant.strip() != '/':
            parts = consonant.split('/')
            for part in parts:
                expanded_results.append({
                    '汉字': row['汉字'],
                    '音标': row['音标'],
                    '声韵': part.strip()
                })
        else:
            expanded_results.append(row)
    # 用新的列表覆盖旧的结果
    result_df = pd.DataFrame(expanded_results)

    # 替换 ε 为 ɛ（如果有）
    # result_df['声韵'] = result_df['声韵'].str.replace('ε', 'ɛ', regex=False)
    replacements = {
        'ε': 'ɛ', "α": "ɑ", "ʯ": "ʮ", "∅": "ø",
        "ã": "ã", "ẽ": "ẽ", "ĩ": "ĩ", "ỹ": "ỹ", "õ": "õ", "ʱ": "ʰ"
    }
    for old, new in replacements.items():
        result_df['声韵'] = result_df['声韵'].str.replace(old, new, regex=True)

    return result_df


import pandas as pd
import re


def get_consonants_from_tsv(tsv_file_path: str, char_list: list) -> pd.DataFrame:
    """
    从TSV文件中提取与字列表匹配的所有汉字及其对应的声母。

    tsv_file_path: TSV文件路径
    char_list: 要查找的汉字列表

    返回: 包含匹配的汉字和声母的DataFrame
    """

    # 读取TSV文件
    tsv_df = pd.read_csv(tsv_file_path, sep="\t")

    if '#漢字' not in tsv_df.columns:
        print("错误：找不到 '#漢字' 列，请检查文件结构！")
        return pd.DataFrame()  # 返回空的 DataFrame，避免后续错误

    # 如果 char_list 为 'all'，获取所有汉字并去重，忽略 "□" 和 "□ □"
    if char_list == "all":
        char_list = tsv_df['#漢字'].drop_duplicates().tolist()
        char_list = [char for char in char_list if char not in ["□", "□"]]  # 排除 "□" 和 "□ □"
    else:
        char_list = list(dict.fromkeys(char_list))  # 保持顺序去重

    # 存储匹配结果
    matched_results = []

    # 遍历字列表
    for char in char_list:
        # 查找对应汉字的音标
        matched_rows = tsv_df[tsv_df['#漢字'] == char]

        if not matched_rows.empty:
            # 对于每个匹配的汉字，遍历所有音标
            for index, row in matched_rows.iterrows():
                phonetic = row['音標']

                # 如果音标为空，跳过
                if phonetic is None or (isinstance(phonetic, float) and math.isnan(phonetic)):
                    continue
                # print(phonetic)
                if isinstance(phonetic, str) and phonetic.isdigit():
                    continue
                # 如果是字符串且开头是数字，跳过（新增）
                if isinstance(phonetic, str) and phonetic and phonetic[0].isdigit():
                    continue

                if not re.search(vowel_pattern, re.split(r"\d", phonetic)[0]):
                    vowel_new = r"([mnŋȵƞʋvʒlf])"  # 有的点把ɿ识别为了fl 酌情加入该列表
                    if phonetic[0] in ['l', 'f']:
                        consonant = phonetic[0]
                    elif re.match(vowel_new, phonetic[0]):
                        consonant = "∅"
                    elif not re.search(vowel_new, phonetic):
                        consonant = f"报错：{phonetic}"
                    else:
                        consonant = ""
                        for char in phonetic:
                            if re.match(vowel_new, char) or re.match(r'\d', char):
                                break  # 一旦遇到元音，停止
                            consonant += char  # 否则，添加字符到声母部分
                else:
                    # 1. 判断开头是否是元音（如果是，视为零声母）
                    if re.match(vowel_pattern, phonetic[0]):
                        consonant = "∅"
                    # # 2. 如果音标中没有元音，而且开头是 m/n/ŋ，则视为零声母
                    # elif not re.search(vowel_pattern, phonetic) and phonetic[0] in ['m', 'n', 'ŋ']:
                    #     consonant = "∅"
                    # elif not re.search(vowel_pattern, phonetic):
                    #     # 3. 如果没有元音，提取开头的第一个字符作为声母
                    #     consonant = phonetic[0]
                    elif ('j' in phonetic[1:] or 'ʲ' in phonetic[1:]):
                        consonant = ""
                        for char in phonetic:
                            if re.match(vowel_pattern, char) or char in ('j', 'ʲ'):
                                break
                            consonant += char
                    else:
                        # 4. 否则，提取第一个字符到第一个元音之间的部分作为声母
                        consonant = ""
                        for char in phonetic:
                            if re.match(vowel_pattern, char):
                                break  # 一旦遇到元音，停止
                            consonant += char  # 否则，添加字符到声母部分
                            consonant = re.sub(r"\d", "", consonant)

                # 存储结果
                matched_results.append({'汉字': row['#漢字'], '音标': phonetic, '声韵': consonant})

    # 拆分包含 "/" 的声韵为两个记录
    expanded_results = []
    for row in matched_results:
        consonant = row['声韵']
        if '/' in consonant and consonant.strip() != '/':
            parts = consonant.split('/')
            for part in parts:
                expanded_results.append({
                    '汉字': row['汉字'],
                    '音标': row['音标'],
                    '声韵': part.strip()
                })
        else:
            expanded_results.append(row)
    # 用新的列表覆盖旧的结果
    result_df = pd.DataFrame(expanded_results)

    # 替换 ε 为 ɛ（如果有）
    replacements = {
        '∫': 'ʃ', 'th': 'tʰ', 'kh': 'kʰ', 'ph': 'pʰ',
        'tsh': 'tsʰ', "ς": "ɕ", 'ts': 'ʦ', 'tʃ': 'ʧ', 'tɕ': 'ʨ',
        "∨": "v", "ł": "ɬ", "tʰs": "ʦʰ"
    }
    for old, new in replacements.items():
        result_df['声韵'] = result_df['声韵'].str.replace(old, new, regex=True)

    return result_df


def get_tones_from_tsv(tsv_file_path: str, char_list: list) -> pd.DataFrame:
    """
    从TSV文件中提取与字列表匹配的所有汉字及其对应的声调。

    tsv_file_path: TSV文件路径
    char_list: 要查找的汉字列表

    返回: 包含匹配的汉字、音标和声调的DataFrame
    """
    # 音典声调映射
    tone_map_yindian = {
        "1": "陰平", "1a": "陰平甲", "1b": "陰平乙", "1A": "陰平甲", "1B": "陰平乙",
        "2": "陽平", "2a": "陽平甲", "2b": "陽平乙", "2A": "陽平甲", "2B": "陽平乙",
        "3": "陰上", "3a": "陰上甲", "3b": "陰上乙", "3A": "陰上甲", "3B": "陰上乙",
        "4": "陽上", "4a": "陽上甲", "4b": "陽上乙", "4A": "陽上甲", "4B": "陽上乙",
        "5": "陰去", "5a": "陰去甲", "5b": "陰去乙", "5A": "陰去甲", "5B": "陰去乙",
        "6": "陽去", "6a": "陽去甲", "6b": "陽去乙", "6A": "陽去甲", "6B": "陽去乙",
        "7": "陰入", "7a": "上陰入", "7b": "下陰入", "7c": "陰入丙", "7A": "上陰入", "7B": "下陰入",
        "8": "陽入", "8a": "上陽入", "8b": "下陽入", "8A": "上陽入", "8B": "下陽入",
        "9": "變調", "9a": "變調1", "9b": "變調2", "0": "變調", "10": "輕聲", "輕聲": "輕聲"
    }

    # 粵拼声调映射
    tone_map_jyutping = {
        "1": "陰平", "2": "陰上", "3": "陰去", "4": "陽平", "5": "陽上", "6": "陽去",
        "7": "上陰入", "8": "下陰入", "9": "陽入", "10": "下陽入", "0": "變調"
    }

    # 读取TSV文件
    tsv_df = pd.read_csv(tsv_file_path, sep="\t")

    if '#漢字' not in tsv_df.columns or '音標' not in tsv_df.columns:
        print("错误：文件缺少必要的 '#漢字' 或 '音標' 列！")
        return pd.DataFrame()

    # 获取所有汉字（去除特殊字符）
    if char_list == "all":
        char_list = tsv_df['#漢字'].drop_duplicates().tolist()
        char_list = [char for char in char_list if char not in ["□", "□ □"]]
    else:
        char_list = list(dict.fromkeys(char_list))  # 去重保持顺序

    # 判斷使用哪個聲調系統（根據“時”與“窮”）
    def extract_tone_number(char: str) -> str:
        row = tsv_df[tsv_df['#漢字'] == char]
        if not row.empty:
            phonetic = str(row.iloc[0]['音標'])
            match = re.search(r"(\d+)", phonetic)
            if match:
                return match.group(1).lstrip("0")
        return None

    tone_shi = extract_tone_number("時")
    tone_qiong = extract_tone_number("窮")

    # 判斷邏輯
    if "2" in [tone_shi, tone_qiong]:
        reference_tone_map = tone_map_yindian
    elif all(tone in ["4", None] for tone in [tone_shi, tone_qiong]):
        reference_tone_map = tone_map_jyutping
    else:
        reference_tone_map = tone_map_yindian

    results = []

    for char in char_list:
        matched_rows = tsv_df[tsv_df['#漢字'] == char]
        if not matched_rows.empty:
            for _, row in matched_rows.iterrows():
                phonetic = str(row['音標'])
                if not phonetic or phonetic.strip() == "":
                    continue

                # 提取结尾的数字 + 可选的一个字母
                match = re.search(r"(\d+[a-z]?)$", phonetic)
                if match:
                    tone_code = match.group(1).lstrip("0")  # 移除前導0以兼容 "03" -> "3"
                    tone_name = reference_tone_map.get(tone_code, tone_map_yindian.get(tone_code, "未知"))
                    results.append({'汉字': row['#漢字'], '音标': phonetic, '声韵': tone_name})

    return pd.DataFrame(results)


# # # 本地路径与查询字列表
# tsv_file = r"C:\Users\joengzaang\myfiles\杂文件\声韵处理\output\通東餘東.tsv"
# tsv_file = r"C:\Users\joengzaang\myfiles\杂文件\声韵处理\output\1890會城.tsv"
# # char_list = ["木", "好", "忽"]
char_list = "all"
#
# # 调用函数并打印结果
# result = get_consonants_from_tsv(tsv_file, char_list)
# pd.set_option('display.max_rows', None)  # 显示所有行
# pd.set_option('display.max_columns', None)  # 显示所有列
# pd.set_option('display.width', None)  # 自动适应宽度
# pd.set_option('display.max_colwidth', None)  # 显示所有列内容（不截断长字符串）
# print(result)
