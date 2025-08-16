import os
import re
import tkinter as tk
from tkinter import filedialog
from docx import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.text.paragraph import Paragraph
from docx.table import Table
from openpyxl import Workbook


def iter_block_items(parent):
    """顺序遍历段落和表格"""
    for child in parent.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)


def extract_data_from_doc(doc):
    results = []

    for block in iter_block_items(doc):
        if isinstance(block, Table):
            table = block
            if len(table.rows) < 3 or len(table.rows[0].cells) < 2:
                continue

            # ✅ 韵母在表格的第一行，第二列开始（全部应该一致）
            rhyme = table.rows[0].cells[1].text.strip()

            # ✅ 声调标签在第二行（第1列之后）
            tone_labels = [
                cell.text.strip() for cell in table.rows[1].cells[1:]
            ]

            # ✅ 数据行从第三行开始
            for row in table.rows[2:]:
                cells = row.cells
                if len(cells) < 2:
                    continue

                shengmu = cells[0].text.strip()
                if not shengmu or not rhyme:
                    continue

                for i, tone in enumerate(tone_labels, start=1):
                    if i >= len(cells):
                        continue
                    chars = cells[i].text.strip()
                    tone_number = ''.join(re.findall(r'\d+', tone))
                    ipa = f"{shengmu}{rhyme}{tone_number}"
                    for char in chars:
                        if re.match(r'[\u4e00-\u9fff]', char):
                            results.append((char, ipa, shengmu, rhyme, tone))
    return results


def generate_excel(data, output_path):
    wb = Workbook()
    ws = wb.active
    ws.title = "一字一音"
    ws.append(["汉字", "ipa", "声母", "韵母", "声调"])
    for row in data:
        ws.append(row)
    wb.save(output_path)


def process_docx_file(file_path):
    print(f"📄 处理文件: {file_path}")
    doc = Document(file_path)
    data = extract_data_from_doc(doc)
    if not data:
        print("⚠️ 无数据提取")
        return

    base_dir = os.path.dirname(file_path)

    def clean_filename(name):
        for word in ["廣西僮族自治區", "同音字表", "表"]:
            name = name.replace(word, "")
        return name.strip()

    raw_name = os.path.splitext(os.path.basename(file_path))[0]
    base_name = clean_filename(raw_name)
    output_path = os.path.join(base_dir, f"{base_name}.xlsx")

    generate_excel(data, output_path)
    print(f"✅ 已保存：{output_path}")


def main():
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(
        title="选择一个或多个 Word 文件",
        filetypes=[("Word 文件", "*.docx")]
    )

    if not file_paths:
        print("❌ 未选择任何文件")
        return

    for file_path in file_paths:
        process_docx_file(file_path)


if __name__ == "__main__":
    main()
