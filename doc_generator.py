# -*- coding: utf-8 -*-
"""近隣説明会 届出書類 Word生成モジュール
東京都の様式をベースに以下を生成:
  1. 標識設置届（建築計画のお知らせ）
  2. 近隣説明報告書
  3. 工事のお知らせ（住民配布用チラシ）
  4. 近隣説明範囲図（地図付きWord）
"""

import os
from datetime import datetime
from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn


# ========== ユーティリティ ==========

def _set_cell(cell, text, font_size=10, bold=False, align=WD_ALIGN_PARAGRAPH.LEFT):
    """セルにテキストを設定"""
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = align
    run = p.add_run(str(text))
    run.font.size = Pt(font_size)
    run.font.name = "游ゴシック"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "游ゴシック")
    run.bold = bold


def _add_heading_paragraph(doc, text, font_size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER):
    """見出し段落を追加"""
    p = doc.add_paragraph()
    p.alignment = align
    run = p.add_run(text)
    run.font.size = Pt(font_size)
    run.font.name = "游ゴシック"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "游ゴシック")
    run.bold = bold
    return p


def _add_body_paragraph(doc, text, font_size=10.5, bold=False, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=6):
    """本文段落を追加"""
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    run = p.add_run(text)
    run.font.size = Pt(font_size)
    run.font.name = "游ゴシック"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "游ゴシック")
    run.bold = bold
    return p


def _set_table_borders(table):
    """テーブルに罫線を設定"""
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else tbl._add_tblPr()
    borders = tblPr.makeelement(qn("w:tblBorders"), {})
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = borders.makeelement(
            qn(f"w:{edge}"),
            {qn("w:val"): "single", qn("w:sz"): "4", qn("w:space"): "0", qn("w:color"): "000000"},
        )
        borders.append(element)
    tblPr.append(borders)


# ========== 1. 標識設置届 ==========

def generate_sign_notice(data, output_path):
    """標識設置届（建築計画のお知らせ）を生成
    東京都中高層建築物紛争予防条例 第2号様式ベース
    """
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

    # ヘッダー
    _add_heading_paragraph(doc, "標 識 設 置 届", font_size=18)
    _add_body_paragraph(doc, f"（東京都中高層建築物の建築に係る紛争の予防と調整に関する条例第6条の規定による届出）",
                        font_size=9, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)

    # 日付・宛先
    _add_body_paragraph(doc, f"　　　　　　　　　　　　　　　　　　　　　　　　{data.get('submit_date', '令和　年　月　日')}")
    _add_body_paragraph(doc, f"　{data.get('ward_name', '○○')}区長　殿")
    _add_body_paragraph(doc, "")

    # 届出者情報
    _add_body_paragraph(doc, f"　届出者　住所　{data.get('applicant_address', '')}")
    _add_body_paragraph(doc, f"　　　　　氏名　{data.get('applicant_name', '')}　　　　　　印")
    _add_body_paragraph(doc, f"　　　　　電話　{data.get('applicant_tel', '')}")
    _add_body_paragraph(doc, "")
    _add_body_paragraph(doc, "　下記のとおり標識を設置しましたので届け出ます。", space_after=12)

    # メインテーブル
    rows_data = [
        ("建築物の名称", data.get("building_name", "")),
        ("建築場所", data.get("site_address", "")),
        ("用途", data.get("building_use", "")),
        ("敷地面積", data.get("site_area", "") + " ㎡"),
        ("建築面積", data.get("building_area", "") + " ㎡"),
        ("延べ面積", data.get("total_floor_area", "") + " ㎡"),
        ("構造", data.get("structure", "")),
        ("階数", f"地上 {data.get('floors_above', '')} 階　地下 {data.get('floors_below', '')} 階"),
        ("高さ", data.get("height", "") + " m"),
        ("着工予定日", data.get("start_date", "")),
        ("完了予定日", data.get("end_date", "")),
        ("設計者", f"{data.get('designer_name', '')}　TEL: {data.get('designer_tel', '')}"),
        ("施工者", f"{data.get('constructor_name', '')}　TEL: {data.get('constructor_tel', '')}"),
        ("標識設置年月日", data.get("sign_install_date", "")),
        ("標識設置場所", data.get("sign_location", "建築予定地の道路に面する見やすい場所")),
    ]

    table = doc.add_table(rows=len(rows_data), cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    _set_table_borders(table)

    for i, (label, value) in enumerate(rows_data):
        _set_cell(table.cell(i, 0), label, font_size=10, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        _set_cell(table.cell(i, 1), value, font_size=10)
        table.cell(i, 0).width = Cm(4.0)
        table.cell(i, 1).width = Cm(12.0)

    _add_body_paragraph(doc, "")
    _add_body_paragraph(doc, "備考：本届出書には、案内図及び配置図を添付すること。", font_size=9)

    doc.save(output_path)
    return output_path


# ========== 2. 近隣説明報告書 ==========

def generate_explanation_report(data, output_path):
    """近隣説明報告書を生成"""
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

    _add_heading_paragraph(doc, "近 隣 説 明 報 告 書", font_size=18)
    _add_body_paragraph(doc, "", space_after=6)

    _add_body_paragraph(doc, f"　　　　　　　　　　　　　　　　　　　　　　　　{data.get('submit_date', '令和　年　月　日')}")
    _add_body_paragraph(doc, f"　{data.get('ward_name', '○○')}区長　殿")
    _add_body_paragraph(doc, "")
    _add_body_paragraph(doc, f"　報告者　住所　{data.get('applicant_address', '')}")
    _add_body_paragraph(doc, f"　　　　　氏名　{data.get('applicant_name', '')}　　　　　　印")
    _add_body_paragraph(doc, f"　　　　　電話　{data.get('applicant_tel', '')}")
    _add_body_paragraph(doc, "")
    _add_body_paragraph(doc, "　下記建築計画について、近隣関係住民に対し説明を行いましたので報告します。", space_after=12)

    # 建築計画概要
    _add_body_paragraph(doc, "１．建築計画の概要", bold=True, space_after=6)
    overview_rows = [
        ("建築物の名称", data.get("building_name", "")),
        ("建築場所", data.get("site_address", "")),
        ("用途", data.get("building_use", "")),
        ("構造・規模", f"{data.get('structure', '')}　地上{data.get('floors_above', '')}階 地下{data.get('floors_below', '')}階"),
        ("高さ", data.get("height", "") + " m"),
        ("着工予定日", data.get("start_date", "")),
        ("完了予定日", data.get("end_date", "")),
    ]

    table1 = doc.add_table(rows=len(overview_rows), cols=2)
    table1.alignment = WD_TABLE_ALIGNMENT.CENTER
    _set_table_borders(table1)
    for i, (label, value) in enumerate(overview_rows):
        _set_cell(table1.cell(i, 0), label, font_size=10, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        _set_cell(table1.cell(i, 1), value, font_size=10)
        table1.cell(i, 0).width = Cm(4.0)
        table1.cell(i, 1).width = Cm(12.0)

    _add_body_paragraph(doc, "", space_after=6)

    # 説明の実施状況
    _add_body_paragraph(doc, "２．説明の実施状況", bold=True, space_after=6)
    explain_rows = [
        ("説明実施日", data.get("explanation_date", "")),
        ("説明方法", data.get("explanation_method", "個別訪問による説明")),
        ("説明範囲", data.get("explanation_range", f"建築予定地から半径{data.get('radius_m', 50)}m以内の近隣住民")),
        ("説明対象戸数", data.get("target_count", "") + " 戸"),
        ("説明済み戸数", data.get("explained_count", "") + " 戸"),
        ("不在等未説明", data.get("unexplained_count", "") + " 戸"),
    ]

    table2 = doc.add_table(rows=len(explain_rows), cols=2)
    table2.alignment = WD_TABLE_ALIGNMENT.CENTER
    _set_table_borders(table2)
    for i, (label, value) in enumerate(explain_rows):
        _set_cell(table2.cell(i, 0), label, font_size=10, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        _set_cell(table2.cell(i, 1), value, font_size=10)
        table2.cell(i, 0).width = Cm(4.0)
        table2.cell(i, 1).width = Cm(12.0)

    _add_body_paragraph(doc, "", space_after=6)

    # 住民からの意見・要望
    _add_body_paragraph(doc, "３．近隣関係住民からの意見・要望とその対応", bold=True, space_after=6)
    opinions = data.get("opinions", "特になし")
    _add_body_paragraph(doc, f"　{opinions}", space_after=12)

    # 添付書類
    _add_body_paragraph(doc, "添付書類", bold=True, font_size=9)
    _add_body_paragraph(doc, "　１．近隣説明範囲図", font_size=9)
    _add_body_paragraph(doc, "　２．説明配布資料（工事のお知らせ）の写し", font_size=9)

    doc.save(output_path)
    return output_path


# ========== 3. 工事のお知らせ（住民配布チラシ） ==========

def generate_construction_notice(data, output_path):
    """工事のお知らせ（住民配布用チラシ）を生成"""
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

    _add_heading_paragraph(doc, "工 事 の お 知 ら せ", font_size=22)
    _add_body_paragraph(doc, "", space_after=12)

    _add_body_paragraph(doc, "近隣の皆様へ", font_size=12, bold=True, space_after=12)

    # 挨拶文
    greeting = data.get("greeting_text",
        "平素は格別のご理解を賜り、厚く御礼申し上げます。\n"
        "このたび、下記のとおり工事を実施させていただくこととなりました。\n"
        "工事期間中は、騒音・振動等でご迷惑をおかけいたしますが、\n"
        "安全管理には十分注意して施工いたしますので、何卒ご理解ご協力のほど\n"
        "よろしくお願い申し上げます。"
    )
    _add_body_paragraph(doc, greeting, font_size=10.5, space_after=16)

    _add_body_paragraph(doc, "記", font_size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)

    # 工事概要テーブル
    notice_rows = [
        ("工事名称", data.get("site_name", "")),
        ("工事場所", data.get("site_address", "")),
        ("工事内容", data.get("work_content", "")),
        ("工事期間", f"{data.get('start_date', '')} ～ {data.get('end_date', '')}"),
        ("作業時間", data.get("work_hours", "午前8時00分 ～ 午後5時00分")),
        ("休工日", data.get("holidays", "日曜日・祝日")),
        ("施工者", data.get("constructor_name", "")),
        ("現場責任者", data.get("site_manager", "")),
        ("連絡先", data.get("constructor_tel", "")),
    ]

    # 発注者がある場合
    if data.get("client_name"):
        notice_rows.insert(0, ("発注者", data.get("client_name", "")))

    table = doc.add_table(rows=len(notice_rows), cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    _set_table_borders(table)

    for i, (label, value) in enumerate(notice_rows):
        _set_cell(table.cell(i, 0), label, font_size=11, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        _set_cell(table.cell(i, 1), value, font_size=11)
        table.cell(i, 0).width = Cm(3.5)
        table.cell(i, 1).width = Cm(12.5)

    _add_body_paragraph(doc, "", space_after=16)

    # 安全対策
    safety = data.get("safety_measures",
        "・工事車両の出入りには誘導員を配置いたします。\n"
        "・粉塵対策として散水・養生を徹底いたします。\n"
        "・騒音・振動が発生する作業は、事前にお知らせいたします。"
    )
    _add_body_paragraph(doc, "【安全対策について】", font_size=10, bold=True, space_after=4)
    _add_body_paragraph(doc, safety, font_size=10, space_after=16)

    # 問い合わせ先
    _add_body_paragraph(doc, "【お問い合わせ先】", font_size=10, bold=True, space_after=4)
    contact = (
        f"　{data.get('constructor_name', '')}\n"
        f"　現場責任者: {data.get('site_manager', '')}\n"
        f"　電話: {data.get('constructor_tel', '')}"
    )
    _add_body_paragraph(doc, contact, font_size=10, space_after=12)

    # 日付・発行者
    _add_body_paragraph(doc, f"　　　　　　　　　　　　　　　　　　　{data.get('submit_date', '令和　年　月　日')}")
    _add_body_paragraph(doc, f"　　　　　　　　　　　　　　　　　　　{data.get('constructor_name', '')}")

    doc.save(output_path)
    return output_path


# ========== 4. 近隣説明範囲図（Word版） ==========

def generate_map_document(data, map_png_path, output_path):
    """近隣説明範囲図をWord文書として生成（地図画像埋め込み）"""
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(29.7)  # A4横
    section.page_height = Cm(21.0)
    section.top_margin = Cm(1.5)
    section.bottom_margin = Cm(1.5)
    section.left_margin = Cm(2.0)
    section.right_margin = Cm(2.0)

    _add_heading_paragraph(doc, "近 隣 説 明 範 囲 図", font_size=18)
    _add_body_paragraph(doc, "", space_after=4)

    # 地図画像
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(map_png_path, width=Cm(24.0))

    _add_body_paragraph(doc, "", space_after=4)

    # 情報テーブル
    info_rows = [
        ("工事名称", data.get("site_name", "")),
        ("工事場所", data.get("site_address", "")),
        ("説明範囲", f"工事現場から半径 {data.get('radius_m', 50)}m 以内"),
        ("施工者", data.get("constructor_name", "")),
    ]
    table = doc.add_table(rows=len(info_rows), cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    _set_table_borders(table)
    for i, (label, value) in enumerate(info_rows):
        _set_cell(table.cell(i, 0), label, font_size=10, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        _set_cell(table.cell(i, 1), value, font_size=10)
        table.cell(i, 0).width = Cm(3.5)
        table.cell(i, 1).width = Cm(22.0)

    doc.save(output_path)
    return output_path
