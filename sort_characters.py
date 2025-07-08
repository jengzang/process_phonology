def processing_examples_vowels(tsv_df, vowel_file_path):
    import pandas as pd
    import re
    from collections import Counter

    # 定义元音列表
    vowels = ['i', 'y', 'ɨ', 'ʉ', 'ɯ', 'u', 'ɪ', 'ʏ', 'ɿ', 'ʅ', 'ʊ',
              'e', 'ø', 'ɘ', 'ə', 'ɵ', 'ɤ', 'o', 'ɛ', 'œ', 'ɜ', 'ɞ',
              'ʌ', 'ɔ', 'æ', 'a', 'ɶ', 'ɑ', 'ɒ', 'ɐ', 'ε', 'ᴀ']

    # 元音正则表达式
    vowel_pattern = r"[iyɨʉɯuɪʏɿʅʅɭıɪſɩɷʮɥʯʊeɘɵəɤoɛεɝɚᴇœɜɞʌɔæaɶɑɒᴀɐãẽĩỹõʒúαᵊⁱ◌∅ø]"
    all_results = []

    # 检查 '#漢字' 列是否存在
    if '#漢字' not in tsv_df.columns:
        print("错误：找不到 '#漢字' 列，请检查文件结构！")
        return pd.DataFrame()

    # 读取例字数据
    example_df = pd.read_excel(vowel_file_path)

    # 遍历每一行例字
    for index, row in example_df.iterrows():
        cell_value = row['例字']
        if pd.isnull(cell_value) or cell_value.strip() == "":
            print(f"第 {index} 行的 '例字' 为空，跳过")  # 调试输出
            all_results.append({"例字": row['例字'], "声韵": "", "批注": ""})
            continue

        rhymes_parts = []
        annotation_parts = []
        blocks = cell_value.split('/') if '/' in cell_value else [cell_value]

        for part in blocks:
            rhymes = []
            rhymes_with_characters = []

            for char in part:
                if char in tsv_df['#漢字'].values:
                    phonetics = tsv_df[tsv_df['#漢字'] == char]['音標'].values
                    for phonetic in phonetics:
                        if not phonetic:
                            continue

                        # 去除括号内容
                        phonetic = re.sub(r'[(){}]', '', phonetic)

                        # 以 / 分段
                        segments = phonetic.split('/')
                        for segment in segments:
                            if not segment.strip():
                                continue

                            block_rhymes = []
                            vowel_found = False

                            # 提取韵母：从第一个元音开始到遇到数字或空格为止
                            for ch in segment:
                                if re.match(vowel_pattern, ch) and not vowel_found:
                                    vowel_found = True
                                    block_rhymes.append(ch)
                                elif vowel_found and (ch.isdigit() or ch.isspace()):
                                    break
                                elif vowel_found:
                                    block_rhymes.append(ch)

                            if block_rhymes:
                                rhyme_str = ''.join(block_rhymes)
                                rhymes.append(rhyme_str)
                                rhymes_with_characters.append(f"{char}: {rhyme_str}")

            # 如果没有提取出韵母
            if not rhymes:
                print(f"第 {index} 行的 {part} 没有韵母，跳过")  # 调试输出
                rhymes_parts.append("")
                annotation_parts.append("")
                continue

            # 统计韵母出现次数
            rhyme_count = Counter(rhymes)
            most_common_rhyme, _ = rhyme_count.most_common(1)[0]

            # 构建与最常见韵母不同的批注
            different_rhymes = []
            for rhyme, count in rhyme_count.items():
                if rhyme != most_common_rhyme:
                    chars = [item.split(': ')[0] for item in rhymes_with_characters if item.split(': ')[1] == rhyme]
                    different_rhymes.append(f"{rhyme}: {','.join(chars)}")

            annotation = "，".join(different_rhymes) if different_rhymes else ""
            rhymes_parts.append(most_common_rhyme)
            annotation_parts.append(annotation)

        # 存储结果
        all_results.append({
            "例字": row['例字'],
            "声韵": "/".join(rhymes_parts),
            "批注": " ".join(annotation_parts)
        })

    return pd.DataFrame(all_results)


def processing_examples_consonants(tsv_df, vowel_file_path):
    import pandas as pd
    import re
    from collections import Counter

    # 定义元音列表
    vowels = ['i', 'y', 'ɨ', 'ʉ', 'ɯ', 'u', 'ɪ', 'ʏ', 'ɿ', 'ʅ', 'ʊ',
              'e', 'ø', 'ɘ', 'ə', 'ɵ', 'ɤ', 'o', 'ɛ', 'œ', 'ɜ', 'ɞ',
              'ʌ', 'ɔ', 'æ', 'a', 'ɶ', 'ɑ', 'ɒ', 'ɐ']

    vowel_pattern = r"([iyɨʉɯuɪʏɿʅʊeøɘəɵɤoɛœɜɞʌɔæaɶɑɒɐ])"
    all_results = []

    if '#漢字' not in tsv_df.columns:
        print("错误：找不到 '#漢字' 列，请检查文件结构！")
        return pd.DataFrame()

    example_df = pd.read_excel(vowel_file_path)

    for index, row in example_df.iterrows():
        cell_value = row['例字']
        if pd.isnull(cell_value) or cell_value.strip() == "":
            print(f"第 {index} 行的 '例字' 为空，跳过")
            all_results.append({"例字": row['例字'], "声韵": "", "批注": ""})
            continue

        consonants_parts = []
        annotation_parts = []
        blocks = cell_value.split('/') if '/' in cell_value else [cell_value]

        for part in blocks:
            consonants = []
            consonants_with_characters = []

            for char in part:
                if char in tsv_df['#漢字'].values:
                    matched_rows = tsv_df[tsv_df['#漢字'] == char]
                    for _, match_row in matched_rows.iterrows():
                        phonetic = match_row['音標']
                        if not phonetic:
                            continue

                        phonetic = re.sub(r'[(){}]', '', phonetic)  # 去除括号等

                        # 提取声母逻辑
                        if re.match(vowel_pattern, phonetic[0]):
                            consonant = "∅"
                        elif not re.search(vowel_pattern, phonetic) and phonetic[0] in ['m', 'n', 'ŋ']:
                            consonant = "∅"
                        elif not re.search(vowel_pattern, phonetic):
                            consonant = phonetic[0]
                        else:
                            consonant = ""
                            for ch in phonetic:
                                if re.match(vowel_pattern, ch):
                                    break
                                consonant += ch

                        consonants.append(consonant)
                        consonants_with_characters.append(f"{char}: {consonant}")

            if not consonants:
                print(f"第 {index} 行的 {part} 没有声母，跳过")
                consonants_parts.append("")
                annotation_parts.append("")
                continue

            consonant_count = Counter(consonants)
            most_common_consonant, _ = consonant_count.most_common(1)[0]

            different_consonants = []
            for cons, count in consonant_count.items():
                if cons != most_common_consonant:
                    chars = [item.split(': ')[0] for item in consonants_with_characters if item.split(': ')[1] == cons]
                    different_consonants.append(f"{cons}: {','.join(chars)}")

            annotation = "，".join(different_consonants) if different_consonants else ""
            consonants_parts.append(most_common_consonant)
            annotation_parts.append(annotation)

        all_results.append({
            "例字": row['例字'],
            "声韵": "/".join(consonants_parts),
            "批注": " ".join(annotation_parts)
        })

    return pd.DataFrame(all_results)
