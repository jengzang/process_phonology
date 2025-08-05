import os
import re

import pandas as pd

# === 替换规则表 ===
replace_data = [
    # 韻腹
    ['aa', 'a', 'wf'], ['a', 'ɐ', 'wf'], ['e', 'ɛ', 'wf'], ['ea', 'ə', 'wf'],['uu', 'ʊ', 'wf'],
    ['oe', 'œ', 'wf'], ['eo', 'ɵ', 'wf'], ['y', 'y', 'wf'], ['o', 'ɔ', 'wf'],
    ['uu', 'ʊ', 'wf'], ['ii', 'ɪ', 'wf'],
    ['or', 'ɤ', 'wf'], ['ar', 'ɑ', 'wf'], ['dd', 'ɗ', 'wf'],
    # ['uu', 'u', 'wf'], ['u', 'ʊ', 'wf'],
    # 聲母
    ['ng', 'ŋ', 'sm'], ['nj', 'ȵ', 'sm'], ['sl', 'ɬ', 'sm'],
    ['th', 'θ', 'sm'], ['bb', 'ɓ', 'sm'], ['dd', 'ɗ', 'sm'],
    ['zh', 'ʧ', 'sm'], ['ch', 'ʧʰ', 'sm'], ['sh', 'ʃ', 'sm'],
    ['zj', 'ʨ', 'sm'], ['cj', 'ʨʰ', 'sm'], ['sj', 'ɕ', 'sm'], ['q', 'ʔ', 'sm'],
    ['c', 'ʦʰ', 'sm'], ['z', 'ʦ', 'sm'],  ['d', 't', 'sm'], ['t', 'tʰ', 'sm'],
    ['g', 'k', 'sm'], ['k', 'kʰ', 'sm'], ['b', 'p', 'sm'], ['p', 'pʰ', 'sm'],
    # ['s', 's', 'sm'],
    # 聲調
    ['1', '454', 'jd'], ['2', '33', 'jd'], ['3', '42', 'jd'],
    ['4', '232', 'jd'], ['5', '23', 'jd'], ['6', '21', 'jd'],
    ['7', '5', 'jd'], ['8', '4', 'jd'], ['9', '2', 'jd'], ['10', '22', 'jd'],
    # 韻尾
    ['ng', 'ŋ', 'wm'], ['h', 'ʔ', 'wm'], ['n', 'n', 'wm'], ['m', 'm', 'wm']
]
replace_df = pd.DataFrame(replace_data, columns=['to_replace', 'replacement', 'condition']).astype(str)

# === 文件读取路径 ===
base_path = os.path.dirname(os.path.abspath(__file__))
input_path = os.path.join(base_path, "jyut2ipa.xlsx")
df = pd.read_excel(input_path, dtype=str, keep_default_na=False)
print(f"✅ 已读取文件: {input_path}, 共 {len(df)} 条记录")


# === 清理并提取注释 ===
def clean_and_extract_notes_fixed(text):
    if not text:
        return "", ""
    symbols = re.findall(r'[？?＊*]', text)
    chinese = re.findall(r'[\u4e00-\u9fa5]', text)
    notes = ''.join([c for c in chinese if c != '或'] + symbols)
    cleaned = re.sub(r'[？?＊*]', '', text)
    cleaned = ''.join(c for c in cleaned if c not in chinese or c == '或')
    return cleaned, notes


# === 粤拼拆分 ===
vowels = set('aeuioy')


def split_pinyin(pinyin):
    initial = final = tone = medial = coda = ''
    for ch in pinyin:
        if ch.isdigit():
            tone += ch
        else:
            if tone:
                final += ch
            else:
                initial += ch
    for i, ch in enumerate(initial):
        if ch in vowels:
            final = initial[i:] + final
            initial = initial[:i]
            break
    else:
        # ❗ 如果没有元音，检查是否结尾是 ng/n/m，作为韵母处理
        if initial.endswith(('ng', 'n', 'm')):
            final = initial[-2:] + final if initial.endswith('ng') else initial[-1:] + final
            initial = initial[:-2] if initial.endswith('ng') else initial[:-1]
    # === 新增特殊处理 ===
    if final in ['ng', 'n', 'm']:
        medial = final  # ✅ 作为韵腹处理
        coda = ""
    elif len(final) == 1 and final[0] in vowels:
        medial = final
        coda = ""
    elif len(final) > 1:
        if final[-1] in 'iu' and len([char for char in final if char in vowels]) > 1:
            medial = final[:-1]
            coda = final[-1]
        else:
            medial = "".join([char for char in final if char in vowels])
            coda = "".join([char for char in final if char not in vowels])

    return initial, final, tone, medial, coda


# === 替换规则 ===
def replace(component, condition):
    if not component:
        return ''
    sorted_df = replace_df[replace_df['condition'] == condition].sort_values(
        by='to_replace', key=lambda x: x.str.len(), ascending=False)
    for _, row in sorted_df.iterrows():
        if row['to_replace'] in component:
            result = component.replace(row['to_replace'], row['replacement'])
            print(f"  [{condition}] 替换: {component} → {result}")
            return result
    print(f"  [{condition}] 无替换: {component}")
    return component


# === 主处理逻辑 ===
def process_yutping(text):
    if not text:
        return pd.Series([""] * 11)

    text_cleaned, notes = clean_and_extract_notes_fixed(text)
    print(f"\n🎯 粤拼原始: {text} → 清理: {text_cleaned} | 注释: {notes}")

    parts = re.split(r'(或|/|\||\\)', text_cleaned)
    print(f"🧩 分段结构: {parts}")

    fields = {
        '声母': [], '韵母': [], '音调': [], '韵腹': [], '韵尾': [],
        '声母IPA': [], '韵腹IPA': [], '韵尾IPA': [], '音调IPA': [], 'IPA': []
    }

    for part in parts:
        if part in ['或', '/', '|', '\\']:
            for key in fields:
                fields[key].append(part)
        elif part.strip():
            ini, fin, tone, med, coda = split_pinyin(part)
            print(f"🔍 拆分: {part} => 声母: {ini}, 韵母: {fin}, 音调: {tone}, 韵腹: {med}, 韵尾: {coda}")

            ini_ipa = replace(ini, 'sm') or 'ʔ'
            if not ini_ipa.strip():
                ini_ipa = 'ʔ'
            if med in ['ng', 'n', 'm']:
                med_ipa = replace(med, 'wm')  # ✅ 虽为韵腹，但用韵尾的替换规则
                print("  ✅ 特例: ng/n/m 虽为韵腹，但使用 wm 替换")
            elif med:
                med_ipa = replace(med, 'wf')
            else:
                med_ipa = ''
            coda_ipa = replace(coda, 'wm')
            tone_ipa = replace(tone, 'jd')
            ipa = ini_ipa + med_ipa + coda_ipa + tone_ipa

            fields['声母'].append(ini)
            fields['韵母'].append(fin)
            fields['音调'].append(tone)
            fields['韵腹'].append(med)
            fields['韵尾'].append(coda)
            fields['声母IPA'].append(ini_ipa)
            fields['韵腹IPA'].append(med_ipa)
            fields['韵尾IPA'].append(coda_ipa)
            fields['音调IPA'].append(tone_ipa)
            fields['IPA'].append(ipa)

    def conditional_join(parts):
        valid = [p for p in parts if p not in ['或', '/', '|', '\\'] and p.strip()]
        if len(valid) == 0:
            return ''
        if len(set(valid)) == 1:
            return valid[0]  # 所有有效部分相同，返回一个
        if len(valid) >= 2:
            return ''.join(parts)
        else:
            return ''.join(p for p in parts if p not in ['或', '/', '|', '\\'])

    row_result = [conditional_join(fields[key]) for key in [
        '声母', '韵母', '音调', '韵腹', '韵尾',
        '声母IPA', '韵腹IPA', '韵尾IPA', '音调IPA', 'IPA'
    ]] + [notes]

    return pd.Series(row_result)


# 应用处理
columns = ['声母', '韵母', '音调', '韵腹', '韵尾',
           '声母IPA', '韵腹IPA', '韵尾IPA', '音调IPA', 'IPA', '注释']
df[columns] = df['粤拼'].apply(process_yutping)

# 保存结果
df.to_excel(input_path, index=False, na_rep="")
print(f"\n✅ 已处理完毕并保存至原文件: {input_path}")
