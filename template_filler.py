# -*- coding: utf-8 -*-
"""公式様式テンプレート流し込みエンジン

各区の公式様式（Word/Excel）にデータを流し込んで出力する。
対応していない区は doc_generator.py のフォールバック生成を使用。

方式:
  Word (.docx): テーブル内のラベルテキストを検索 → 隣接する空セルに値を書き込む
  Excel (.xlsx): セル座標を直接指定して値を書き込む
"""

import os
import re
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn

try:
    import openpyxl
except ImportError:
    openpyxl = None


TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")


# ========== ユーティリティ ==========

def _set_cell_text(cell, text):
    """Wordテーブルのセルにテキストを設定（既存書式をなるべく保持）"""
    if not cell.paragraphs:
        return
    p = cell.paragraphs[0]
    for run in p.runs:
        run.text = ""
    if p.runs:
        p.runs[0].text = str(text)
    else:
        run = p.add_run(str(text))
        run.font.name = "游ゴシック"
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "游ゴシック")
        run.font.size = Pt(10)


def _replace_in_cell(cell, old_text, new_text):
    """セル内のテキストを部分置換"""
    for p in cell.paragraphs:
        full_text = p.text
        if old_text in full_text:
            combined = "".join(r.text for r in p.runs)
            replaced = combined.replace(old_text, new_text, 1)
            for i, run in enumerate(p.runs):
                if i == 0:
                    run.text = replaced
                else:
                    run.text = ""
            return True
    return False


def _cell_is_empty(cell):
    """セルが空（全角スペース・改行のみ含む）かどうか"""
    t = cell.text.strip().replace("\u3000", "").replace("\n", "")
    return not t


def _find_value_cell_in_row(row, label_text):
    """行内でラベルテキストを探し、その隣の空セルを返す

    マージされたセルでは同じテキストが複数セルに出現するため、
    ラベルと異なるテキスト（空のセル）を探す。
    """
    cells = list(row.cells)
    # まずラベルが含まれるセルの範囲を特定
    label_end = -1
    for i, cell in enumerate(cells):
        if label_text in cell.text:
            label_end = i

    if label_end < 0:
        return None

    # ラベルの後の空セルを探す
    for i in range(label_end + 1, len(cells)):
        cell = cells[i]
        # ラベルと同じテキスト（マージの繰り返し）はスキップ
        if label_text in cell.text:
            continue
        # 「電話」「㎡」などの固定テキストはスキップ
        t = cell.text.strip()
        if t and not t.startswith("電") and t != "㎡" and "m2" not in t:
            continue
        if _cell_is_empty(cell):
            return cell

    return None


def _find_row_by_label(table, label_pattern):
    """テーブル内でラベルパターンにマッチする行を返す"""
    for ri, row in enumerate(table.rows):
        for cell in row.cells:
            if re.search(label_pattern, cell.text):
                return ri, row
    return None, None


# ========== Word (.docx) 汎用フィラー ==========

# 各区の標識設置届のフィールド定義
# key: ward_name, value: {
#   "table_index": テーブル番号,
#   "labels": [(ラベル検索パターン, データキー), ...],
#   "replacements": [(セル内の古いテキスト, データキー), ...]
# }

SIGN_NOTICE_CONFIG = {
    "品川": {
        "table_index": 0,
        "labels": [
            ("１建築物の名称|１\u3000建築物の名称", "building_name"),
            ("２設計者|２\u3000設計者", "designer_info"),
            ("３施工者|３\u3000施工者", "constructor_info"),
            ("５\u3000主要用途|５ 主要用途", "building_use"),
            ("６\u3000工事種別|６ 工事種別", "construction_type"),
            ("８\u3000高.*さ|８ 高.*さ", "height"),
            ("11\u3000着工予定|11 着工予定", "start_date"),
            ("12\u3000完了予定|12 完了予定", "end_date"),
            ("13\u3000連絡先|13 連絡先", "contact_info"),
        ],
    },
    "渋谷": {
        "table_index": 0,
        "labels": [
            ("１\u3000建築物の名称", "building_name"),
            ("２\u3000設計者", "designer_info"),
            ("３\u3000施工者", "constructor_info"),
            ("４\u3000建築計画に関する連絡先", "contact_info"),
            ("７\u3000主.*用.*途", "building_use"),
            ("１３\u3000着工予定", "start_date"),
        ],
    },
    "墨田": {
        "table_index": 0,
        "labels": [
            ("1\u3000建築物の名称", "building_name"),
            ("2\u3000設計者", "designer_info"),
            ("3\u3000施工者", "constructor_info"),
            ("5\u3000主要用途", "building_use"),
        ],
    },
    "江東": {
        "table_index": 0,
        "labels": [
            ("１\u3000建築物の名称", "building_name"),
            ("２\u3000設計者", "designer_info"),
            ("３\u3000施工者", "constructor_info"),
            ("５\u3000主.*用.*途", "building_use"),
        ],
    },
    "北": {
        "table_index": 1,
        "labels": [
            ("建築物の名称", "building_name"),
            ("設計者住所", "designer_info"),
            ("施工者住所", "constructor_info"),
            ("主要用途", "building_use"),
        ],
    },
    "足立": {
        "table_index": 1,
        "labels": [
            ("１\u3000建築物の名称", "building_name"),
            ("２\u3000設計者", "designer_info"),
            ("３\u3000施工者", "constructor_info"),
            ("５\u3000主.*用.*途", "building_use"),
        ],
    },
    "世田谷": {
        "table_index": 0,
        "labels": [
            ("建築物の名称", "building_name"),
            ("設計者", "designer_info"),
            ("施工者", "constructor_info"),
            ("主要用途|用途", "building_use"),
            ("工事種別", "construction_type"),
            ("高.*さ", "height"),
            ("構.*造", "structure"),
            ("基.*礎.*工", "foundation"),
            ("着工予定", "start_date"),
            ("完了予定|工事完了", "end_date"),
            ("連絡先", "contact_info"),
        ],
    },
    "杉並": {
        "table_index": 0,
        "labels": [
            ("建築物の名称", "building_name"),
            ("設計者", "designer_info"),
            ("施工者", "constructor_info"),
            ("主要用途", "building_use"),
            ("工事種別", "construction_type"),
            ("高.*さ", "height"),
            ("構.*造", "structure"),
            ("基.*礎.*工", "foundation"),
            ("着工予定", "start_date"),
            ("完了予定", "end_date"),
            ("連絡先", "contact_info"),
        ],
    },
    "板橋": {
        "table_index": 0,
        "labels": [
            ("建築物.*名称", "building_name"),
            ("設計者", "designer_info"),
            ("施工者", "constructor_info"),
            ("主要用途|用途", "building_use"),
            ("工事種別", "construction_type"),
            ("高.*さ", "height"),
            ("構.*造", "structure"),
            ("基.*礎.*工", "foundation"),
            ("着工予定", "start_date"),
            ("完了予定", "end_date"),
            ("連絡先", "contact_info"),
        ],
    },
    "江戸川": {
        "table_index": 0,
        "labels": [
            ("建築物.*名称", "building_name"),
            ("設計者", "designer_info"),
            ("施工者", "constructor_info"),
            ("主要用途|用途", "building_use"),
            ("工事種別", "construction_type"),
            ("高.*さ", "height"),
            ("構.*造", "structure"),
            ("基.*礎.*工", "foundation"),
            ("着工予定", "start_date"),
            ("完了予定", "end_date"),
            ("連絡先", "contact_info"),
        ],
    },
    "港": {
        "table_index": 0,
        "labels": [
            ("建築物の名称", "building_name"),
            ("設計者", "designer_info"),
            ("施工者", "constructor_info"),
            ("着工予定", "start_date"),
            ("完了予定", "end_date"),
            ("連絡先", "contact_info"),
        ],
    },
    "目黒": {
        "table_index": 0,
        "labels": [
            ("建築物の名称", "building_name"),
            ("設計者", "designer_info"),
            ("施工者", "constructor_info"),
            ("主要用途", "building_use"),
            ("工事種別", "construction_type"),
            ("高.*さ", "height"),
            ("構.*造", "structure"),
            ("基.*礎.*工", "foundation"),
            ("着工予定", "start_date"),
            ("完了予定", "end_date"),
            ("標識設置日", "sign_install_date"),
        ],
    },
    "荒川": {
        "table_index": 0,
        "labels": [
            ("建築物の名称", "building_name"),
            ("設計者", "designer_info"),
            ("施工者", "constructor_info"),
            ("主要用途", "building_use"),
            ("工事種別", "construction_type"),
            ("高.*さ", "height"),
            ("構.*造", "structure"),
            ("基.*礎.*工", "foundation"),
            ("連絡先", "contact_info"),
        ],
    },
}

REPORT_CONFIG = {
    "品川": {
        "table_index": 0,
        "labels": [
            ("建築物の名称", "building_name"),
        ],
    },
    "渋谷": {
        "table_index": 0,
        "labels": [
            ("１\u3000建築物の名称", "building_name"),
        ],
    },
    "墨田": {
        "table_index": 0,
        "labels": [
            ("建築物の名称", "building_name"),
        ],
    },
    "江東": {
        "table_index": 0,
        "labels": [
            ("建築物の名称", "building_name"),
        ],
    },
    "世田谷": {
        "table_index": 0,
        "labels": [
            ("建築物の名称", "building_name"),
        ],
    },
    "杉並": {
        "table_index": 0,
        "labels": [
            ("建築物の名称", "building_name"),
        ],
    },
    "江戸川": {
        "table_index": 0,
        "labels": [
            ("建築物.*名称", "building_name"),
        ],
    },
    "目黒": {
        "table_index": 0,
        "labels": [
            ("建築物の名称", "building_name"),
        ],
    },
}


def _prepare_data(data):
    """入力データから流し込み用のデータを準備

    テンプレートが必要とする全フィールドを網羅する。
    複合フィールド（designer_info等）は元データから組み立てる。
    """
    designer_name = data.get("designer_name", "")
    designer_tel = data.get("designer_tel", "")
    constructor_name = data.get("constructor_name", "")
    constructor_tel = data.get("constructor_tel", "")
    site_manager = data.get("site_manager", "")

    # 複合フィールド
    designer_info = designer_name
    if designer_tel:
        designer_info = f"{designer_name}  TEL: {designer_tel}"

    constructor_info = constructor_name
    if constructor_tel:
        constructor_info = f"{constructor_name}  TEL: {constructor_tel}"

    contact_info = site_manager
    if constructor_tel:
        contact_info = f"{site_manager}  TEL: {constructor_tel}"

    # 階数フォーマット
    floors_above = data.get("floors_above", "")
    floors_below = data.get("floors_below", "")
    floors_text = ""
    if floors_above or floors_below:
        floors_text = f"地上{floors_above}階"
        if floors_below:
            floors_text += f" 地下{floors_below}階"

    return {
        # === 建物基本情報 ===
        "building_name": data.get("building_name", ""),
        "site_name": data.get("site_name", ""),
        "site_address": data.get("site_address", ""),
        "land_number": data.get("land_number", ""),       # 地名地番
        "building_use": data.get("building_use", ""),
        "structure": data.get("structure", ""),
        "foundation": data.get("foundation", ""),          # 基礎工法
        "construction_type": data.get("construction_type", ""),  # 工事種別
        "height": data.get("height", ""),
        "floors_above": floors_above,
        "floors_below": floors_below,
        "floors_text": floors_text,
        "unit_count": data.get("unit_count", ""),          # 総戸数
        "oneroom_count": data.get("oneroom_count", ""),    # ワンルーム戸数
        "site_area": data.get("site_area", ""),
        "building_area": data.get("building_area", ""),
        "total_floor_area": data.get("total_floor_area", ""),
        "zoning": data.get("zoning", ""),                  # 用途地域
        "fire_zone": data.get("fire_zone", ""),            # 防火地域
        "other_zone": data.get("other_zone", ""),          # その他地域地区
        # === 工期 ===
        "start_date": data.get("start_date", ""),
        "end_date": data.get("end_date", ""),
        "work_hours": data.get("work_hours", ""),
        "holidays": data.get("holidays", ""),
        "work_content": data.get("work_content", ""),
        # === 届出情報 ===
        "submit_date": data.get("submit_date", ""),
        "sign_install_date": data.get("sign_install_date", ""),
        "sign_location": data.get("sign_location", ""),
        # === 関係者 ===
        "applicant_name": data.get("applicant_name", ""),
        "applicant_address": data.get("applicant_address", ""),
        "applicant_tel": data.get("applicant_tel", ""),
        "client_name": data.get("client_name", ""),
        "designer_name": designer_name,
        "designer_info": designer_info,
        "designer_tel": designer_tel,
        "constructor_name": constructor_name,
        "constructor_info": constructor_info,
        "constructor_tel": constructor_tel,
        "site_manager": site_manager,
        "contact_info": contact_info,
        # === 説明報告 ===
        "explanation_date": data.get("explanation_date", ""),
        "explanation_method": data.get("explanation_method", ""),
        "target_count": data.get("target_count", ""),
        "explained_count": data.get("explained_count", ""),
        "unexplained_count": data.get("unexplained_count", ""),
        "opinions": data.get("opinions", ""),
    }


def _find_template_file(ward_name, keywords):
    """テンプレートファイルを検索"""
    ward_dir = os.path.join(TEMPLATES_DIR, f"{ward_name}区")
    if not os.path.isdir(ward_dir):
        return None

    # まず .docx を優先
    for fname in os.listdir(ward_dir):
        if not fname.endswith(".docx"):
            continue
        for kw in keywords:
            if kw in fname:
                return os.path.join(ward_dir, fname)

    # 一括ファイル
    for fname in os.listdir(ward_dir):
        if fname.endswith(".docx") and ("様式" in fname or "申請書類" in fname):
            return os.path.join(ward_dir, fname)

    return None


def _remove_seal_marks(doc):
    """文書内の「印」（押印マーク）を削除する"""
    # 段落内
    for p in doc.paragraphs:
        full = "".join(r.text for r in p.runs)
        if "印" in full:
            cleaned = full.replace("　印", "").replace("印", "")
            for i, run in enumerate(p.runs):
                run.text = cleaned if i == 0 else ""
    # テーブル内
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    full = "".join(r.text for r in p.runs)
                    if "印" in full:
                        cleaned = full.replace("　印", "").replace("印", "")
                        for i, run in enumerate(p.runs):
                            run.text = cleaned if i == 0 else ""


def _fill_docx_by_labels(template_path, config, data, output_path):
    """ラベル検索方式でWordテンプレートにデータを流し込む"""
    doc = Document(template_path)
    fill_data = _prepare_data(data)

    table_idx = config["table_index"]
    if table_idx >= len(doc.tables):
        return None

    table = doc.tables[table_idx]

    for label_pattern, field_name in config["labels"]:
        value = fill_data.get(field_name, "")
        if not value:
            continue

        # テーブル内でラベルを探す
        for ri, row in enumerate(table.rows):
            found = False
            for cell in row.cells:
                if re.search(label_pattern, cell.text):
                    found = True
                    break

            if not found:
                continue

            # この行内で空セルを探して値を書き込む
            cells = list(row.cells)
            # ラベルセルの範囲を特定（マージで同じテキストが繰り返される）
            label_cells = set()
            for ci, cell in enumerate(cells):
                if re.search(label_pattern, cell.text):
                    label_cells.add(ci)

            # ラベルでない空セルに値を書き込む
            wrote = False
            for ci, cell in enumerate(cells):
                if ci in label_cells:
                    continue
                # 前のセルと同じ内容ならマージされたセル、スキップ
                if ci > 0 and cell._element is cells[ci - 1]._element:
                    continue
                # 「電話」「㎡」等の固定テキストはスキップ
                t = cell.text.strip()
                if t and ("電" in t or "㎡" in t or "m2" in t):
                    continue
                if _cell_is_empty(cell):
                    _set_cell_text(cell, value)
                    wrote = True
                    break

            if wrote:
                break  # 次のフィールドへ

    _remove_seal_marks(doc)
    doc.save(output_path)
    return output_path


# ========== Excel (.xlsx) テンプレートフィラー ==========

XLSX_CONFIGS = {
    "豊島": {
        "file": "豊島区/標識設置届.xlsx",
        "sheet": "標識設置届（正）A3",
        "cells": {
            "E19": "building_name",
            "E20": "designer_info",
            "E21": "constructor_info",
            "E22": "site_address",
            "E25": "building_use",
            "I8": "applicant_address",
            "I10": "applicant_name",
            "I12": "applicant_tel",
        },
    },
    "練馬": {
        "file": "練馬区/様式（標識設置届・住民説明報告書等）.xlsx",
        "sheet": "標識設置届",
        "cells": {
            "V18": "building_name",
            "V19": "site_address",
            "V27": "structure",
            "V30": "designer_info",
            "V32": "constructor_info",
            "V35": "contact_info",
        },
    },
    "中野": {
        "file": "中野区/届出様式一式.xlsx",
        "sheet": "標識設置届",
        "cells": {
            "H23": "building_name",
            "H24": "designer_info",
            "H27": "constructor_info",
            "T8": "applicant_address",
            "T10": "applicant_name",
        },
    },
    "文京": {
        "file": "文京区/標識設置届.xlsx",
        "sheet": "表面",
        "cells": {
            "F14": "building_name",
            "F15": "designer_info",
            "F16": "constructor_info",
            "F17": "land_number",
            "F18": "zoning",
            "F19": "other_zone",
            "F20": "building_use",
            "F21": "height",
            "F22": "structure",
            "F23": "unit_count",
            "F25": "site_area",
            "F26": "building_area",
            "F27": "total_floor_area",
            "L20": "construction_type",
        },
    },
    "新宿": {
        "file": "新宿区/標識設置届.xlsx",
        "sheet": "標識設置届",
        "cells": {
            "H23": "building_name",
            "H24": "designer_info",
            "H25": "constructor_info",
            "H26": "land_number",
            "H27": "zoning",
            "H28": "other_zone",
            "H30": "building_use",
            "AB30": "construction_type",
            "H34": "structure",
        },
    },
    "葛飾": {
        "file": "葛飾区/標識設置届.xlsx",
        "sheet": "Sheet3",
        "cells": {
            "J19": "building_name",
            "J20": "site_address",
            "J21": "building_use",
            "J22": "building_area",
            "O21": "site_area",
            "O22": "total_floor_area",
            "J23": "structure",
            "O23": "foundation",
            "J26": "applicant_name",
            "J27": "designer_info",
            "J28": "constructor_info",
        },
    },
}

XLSX_REPORT_CONFIGS = {
    "港": {
        "file": "港区/隣接関係住民説明会等報告書.xlsx",
        "sheet": "Sheet1",
        "cells": {
            "F14": "building_name",
            "F15": "designer_info",
            "F18": "constructor_info",
            "F21": "site_address",
            "F24": "building_use",
        },
    },
    "練馬": {
        "file": "練馬区/様式（標識設置届・住民説明報告書等）.xlsx",
        "sheet": "住民説明報告書",
        "cells": {
            "V17": "building_name",
            "V18": "site_address",
            "V26": "structure",
            "V29": "designer_info",
            "V31": "constructor_info",
            "V33": "contact_info",
        },
    },
    "中野": {
        "file": "中野区/届出様式一式.xlsx",
        "sheet": "説明会等内容報告書(表)",
        "cells": {
            "F21": "site_address",
        },
    },
    "文京": {
        "file": "文京区/説明会等報告書.xlsx",
        "sheet": "説明会報告書（表）",
        "cells": {
            "H17": "building_name",
            "H18": "site_address",
        },
    },
}


def _fill_xlsx_with_config(config, data, output_path):
    """Excel形式テンプレートにデータを流し込む（汎用）"""
    if not openpyxl:
        return None

    template_path = os.path.join(TEMPLATES_DIR, config["file"])
    if not os.path.exists(template_path):
        return None

    wb = openpyxl.load_workbook(template_path)
    sheet_name = config.get("sheet")
    ws = wb[sheet_name] if sheet_name and sheet_name in wb.sheetnames else wb.active

    fill_data = _prepare_data(data)

    for cell_ref, field_name in config["cells"].items():
        value = fill_data.get(field_name, "")
        if value:
            ws[cell_ref] = value

    # Excelシート内の「印」を削除
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str) and "印" in cell.value:
                cell.value = cell.value.replace("　印", "").replace("印", "")

    wb.save(output_path)
    return output_path


# ========== メインAPI ==========

def get_available_templates(ward_name):
    """指定区で利用可能なテンプレートの種類を返す"""
    result = {"sign_notice": None, "report": None}

    if ward_name in SIGN_NOTICE_CONFIG:
        tpl = _find_template_file(ward_name, ["標識", "申請書類", "様式集"])
        if tpl:
            result["sign_notice"] = "docx"

    if ward_name in XLSX_CONFIGS:
        result["sign_notice"] = "xlsx"

    if ward_name in REPORT_CONFIG:
        tpl = _find_template_file(ward_name, ["説明", "報告"])
        if tpl:
            result["report"] = "docx"

    if ward_name in XLSX_REPORT_CONFIGS:
        result["report"] = "xlsx"

    return result


def fill_sign_notice(ward_name, data, output_path):
    """標識設置届を公式テンプレートで生成

    Returns: output_path if template was used, None if fallback needed
    """
    # Excel テンプレート
    config = XLSX_CONFIGS.get(ward_name)
    if config:
        result = _fill_xlsx_with_config(config, data, output_path)
        if result:
            return result

    # Word テンプレート
    config = SIGN_NOTICE_CONFIG.get(ward_name)
    if config:
        template = _find_template_file(ward_name, ["標識", "申請書類", "様式集"])
        if template:
            return _fill_docx_by_labels(template, config, data, output_path)

    return None


def fill_explanation_report(ward_name, data, output_path):
    """説明報告書を公式テンプレートで生成

    Returns: output_path if template was used, None if fallback needed
    """
    # Excel テンプレート
    report_config = XLSX_REPORT_CONFIGS.get(ward_name)
    if report_config:
        result = _fill_xlsx_with_config(report_config, data, output_path)
        if result:
            return result

    # Word テンプレート
    config = REPORT_CONFIG.get(ward_name)
    if config:
        template = _find_template_file(ward_name, ["説明", "報告"])
        if template:
            return _fill_docx_by_labels(template, config, data, output_path)

    return None


# ========== 区ごとの必要フィールド定義 ==========

# フィールドID → 表示名のマスター定義
FIELD_LABELS = {
    "building_name": "建築物の名称",
    "site_address": "建築場所（住居表示）",
    "land_number": "地名地番",
    "building_use": "主要用途",
    "structure": "構造",
    "foundation": "基礎工法",
    "construction_type": "工事種別",
    "height": "高さ（m）",
    "floors_above": "地上階数",
    "floors_below": "地下階数",
    "unit_count": "総住戸数",
    "oneroom_count": "ワンルーム戸数（40㎡未満）",
    "site_area": "敷地面積（㎡）",
    "building_area": "建築面積（㎡）",
    "total_floor_area": "延べ面積（㎡）",
    "zoning": "用途地域",
    "fire_zone": "防火地域",
    "other_zone": "その他の地域・地区",
    "start_date": "着工予定日",
    "end_date": "完了予定日",
    "submit_date": "届出日",
    "sign_install_date": "標識設置日",
    "applicant_name": "届出者（建築主）氏名",
    "applicant_address": "届出者 住所",
    "applicant_tel": "届出者 電話",
    "designer_name": "設計者名",
    "designer_tel": "設計者 電話",
    "constructor_name": "施工者名",
    "constructor_tel": "施工者 電話",
    "site_manager": "現場責任者",
    "explanation_date": "説明実施日",
    "explanation_method": "説明方法",
    "target_count": "説明対象戸数",
    "explained_count": "説明済み戸数",
    "unexplained_count": "未説明戸数",
    "opinions": "住民からの意見・要望",
}


def get_required_fields(ward_name):
    """指定区のテンプレートが必要とするフィールドIDのセットを返す

    Returns:
        dict: {"sign_notice": set of field IDs, "report": set of field IDs}
    """
    sign_fields = set()
    report_fields = set()

    # ラベル→フィールドIDのマッピングから抽出（info系は元フィールドに展開）
    _info_expand = {
        "designer_info": {"designer_name", "designer_tel"},
        "constructor_info": {"constructor_name", "constructor_tel"},
        "contact_info": {"site_manager", "constructor_tel"},
        "floors_text": {"floors_above", "floors_below"},
    }

    def _expand(field_id):
        return _info_expand.get(field_id, {field_id})

    # Word標識設置届
    config = SIGN_NOTICE_CONFIG.get(ward_name)
    if config:
        for _, field_id in config["labels"]:
            sign_fields |= _expand(field_id)

    # Excel標識設置届
    config = XLSX_CONFIGS.get(ward_name)
    if config:
        for _, field_id in config["cells"].items():
            sign_fields |= _expand(field_id)

    # Word報告書
    config = REPORT_CONFIG.get(ward_name)
    if config:
        for _, field_id in config["labels"]:
            report_fields |= _expand(field_id)

    # Excel報告書
    config = XLSX_REPORT_CONFIGS.get(ward_name)
    if config:
        for _, field_id in config["cells"].items():
            report_fields |= _expand(field_id)

    # テンプレートがない場合（汎用生成）でも最低限のフィールドは必要
    if not sign_fields:
        sign_fields = {
            "building_name", "site_address", "building_use", "structure",
            "height", "floors_above", "floors_below",
            "site_area", "building_area", "total_floor_area",
            "start_date", "end_date", "submit_date", "sign_install_date",
            "applicant_name", "applicant_address", "applicant_tel",
            "designer_name", "designer_tel",
            "constructor_name", "constructor_tel",
        }
    if not report_fields:
        report_fields = {
            "building_name", "site_address", "building_use", "structure",
            "height", "floors_above", "floors_below",
            "start_date", "end_date", "submit_date",
            "applicant_name", "applicant_address", "applicant_tel",
            "explanation_date", "explanation_method",
            "target_count", "explained_count", "unexplained_count",
            "opinions",
        }

    return {"sign_notice": sign_fields, "report": report_fields}
