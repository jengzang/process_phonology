import pandas as pd
import re
import math


def extract_all_from_tsv(tsv_file_path: str) -> pd.DataFrame:
    vowel_pattern = r"[iyɨʉɯuɪʏɿʅʅɭıɪſɩɷʮɥʯʊeɘɵəɤoɛεɝɚᴇœɜɞʌɔæaɶɑɒᴀɐãẽĩỹõúαᵘᶷᶤᶶᵚʸᶦᵊⁱ◌∅ø]"

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
    # tone_map_jyutping = {
    #     "1": "陰平", "2": "陰上", "3": "陰去", "4": "陽平", "5": "陽上", "6": "陽去",
    #     "7": "上陰入", "8": "下陰入", "9": "陽入", "10": "下陽入", "0": "變調"
    # }

    df = pd.read_csv(tsv_file_path, sep="\t", dtype=str)
    df.columns = [col.lstrip("#").strip() for col in df.columns]
    df = df.fillna("")

    # 判斷 tone 系統
    # def extract_tone_number(df, char):
    #     row = df[df['漢字'] == char]
    #     if not row.empty:
    #         phonetic = row.iloc[0]['音標']
    #         if isinstance(phonetic, str):
    #             match = re.search(r"(\d+)", phonetic)
    #             if match:
    #                 return match.group(1).lstrip("0")
    #     return None

    # tone_shi = extract_tone_number(df, "時")
    # tone_qiong = extract_tone_number(df, "窮")
    tone_map = tone_map_yindian
    # tone_map = tone_map_yindian if "2" in [tone_shi, tone_qiong] else tone_map_jyutping

    results = []

    for _, row in df.iterrows():
        hanzi = row.get("漢字", "").strip()
        phonetic = row.get("音標", "").strip()
        note = row.get("解釋", "").strip()

        if not hanzi or not phonetic or phonetic == "0" or hanzi == "0":
            continue
        if re.search(r"[□■⬜⬛☐☑☒▯▢▣█�]", hanzi):
            continue
        if phonetic and (isinstance(phonetic, float) and math.isnan(phonetic)):
            continue
        if isinstance(phonetic, str) and phonetic and phonetic[0].isdigit():
            continue

        phonetic_variants = phonetic.split("/") if "/" in phonetic and phonetic.strip() != '/' else [phonetic]

        for phon in phonetic_variants:
            phon = phon.strip()
            # 提取聲調
            tone_match = re.search(r"(\d+[a-zA-Z]?)$", phon)
            tone_code = tone_match.group(1).lstrip("0") if tone_match else ""
            tone = tone_map.get(tone_code, tone_map_yindian.get(tone_code, "未知")) if tone_code else ""

            # 提取聲母
            consonant = ""
            if not re.search(vowel_pattern, re.split(r"\d", phon)[0]):
                vowel_fallback = r"([mnŋȵƞʋvʒlf])"
                if phon[0] in ['l', 'f']:
                    consonant = phon[0]
                elif re.match(vowel_fallback, phon[0]):
                    consonant = "∅"
                elif not re.search(vowel_fallback, phon):
                    consonant = f"報錯：{phon}"
                else:
                    for char in phon:
                        if re.match(vowel_fallback, char) or re.match(r'\d', char):
                            break
                        consonant += char
            else:
                if re.match(vowel_pattern, phon[0]):
                    consonant = "∅"
                elif 'j' in phon[1:] or 'ʲ' in phon[1:]:
                    for char in phon:
                        if re.match(vowel_pattern, char) or char in ('j', 'ʲ'):
                            break
                        consonant += char
                else:
                    for char in phon:
                        if re.match(vowel_pattern, char):
                            break
                        consonant += char
            consonant = re.sub(r"\d", "", consonant)

            # 韻母提取
            all_rhymes = []
            tmp_phon = phon[1:] if phon.startswith("∅") else phon
            if ('j' not in tmp_phon[1:] and 'ʲ' not in tmp_phon[1:]):
                vowel_found = False
                for c in tmp_phon:
                    if re.match(vowel_pattern, c) and not vowel_found:
                        vowel_found = True
                        all_rhymes.append(c)
                    elif vowel_found and (c.isdigit() or c.isspace()):
                        break
                    elif vowel_found:
                        all_rhymes.append(c)
                if not vowel_found and any(c in tmp_phon for c in "mnŋȵƞʋvʒ"):
                    match = re.search(r".*?([mnŋȵƞʋvʒ].*?)(?=\d|\s|$)", tmp_phon)
                    if match:
                        all_rhymes += list(match.group(1))
            else:
                match = re.search(rf"[{vowel_pattern.strip('[]')}jʲ][^\d\s]*", tmp_phon)
                if match:
                    all_rhymes = list(match.group(0))

            rhyme = ''.join(c for c in all_rhymes if not (c.isdigit() or re.match(r'[一-鿿]', c)))
            for old, new in {
                'ε': 'ɛ', "α": "ɑ", "ʯ": "ʮ", "∅": "ø",
                "ã": "ã", "ẽ": "ẽ", "ĩ": "ĩ", "ỹ": "ỹ", "õ": "õ", "ʱ": "ʰ"
            }.items():
                rhyme = rhyme.replace(old, new)

            for old, new in {
                '∫': 'ʃ', 'th': 'tʰ', 'kh': 'kʰ', 'ph': 'pʰ',
                'tsh': 'tsʰ', "ς": "ɕ", 'ts': 'ʦ', 'tʃ': 'ʧ', 'tɕ': 'ʨ',
                "∨": "v", "ł": "ɬ", "tʰs": "ʦʰ", "(ʔ)": "ʔ", "∅": "ʔ"
            }.items():
                consonant = consonant.replace(old, new)

            results.append({
                '汉字': hanzi,
                '音标': phon,
                '声母': consonant,
                '韵母': rhyme,
                '声调': tone,
                '註釋': note
            })

    return pd.DataFrame(results)

# tsv_file = r"C:\Users\joengzaang\myfiles\杂文件\声韵处理\processed\東莞東坑.tsv"
# result = extract_all_from_tsv(tsv_file)
# pd.set_option('display.max_rows', None)  # 显示所有行
# pd.set_option('display.max_columns', None)  # 显示所有列
# pd.set_option('display.width', None)  # 自动适应宽度
# pd.set_option('display.max_colwidth', None)  # 显示所有列内容（不截断长字符串）
# print(result)
