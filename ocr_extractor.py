# -*- coding: utf-8 -*-
"""現場書類OCR抽出モジュール
Gemini API（Vision）でPDF/画像から工事情報を構造化抽出する
"""

import os
import json
import base64

try:
    import google.generativeai as genai
except ImportError:
    genai = None


# 抽出対象フィールドの定義
EXTRACT_FIELDS = {
    "site_name": "工事名称（例: ○○ビル新築工事）",
    "site_address": "工事場所の住所（例: 東京都新宿区西新宿2-8-1）",
    "building_name": "建築物の名称（例: ○○ビル）",
    "building_use": "主要用途（例: 事務所、共同住宅、店舗）",
    "work_content": "工事内容（例: RC造建物の新築工事）",
    "structure": "構造（例: 鉄筋コンクリート造、鉄骨造、木造）",
    "floors_above": "地上階数（数字のみ。例: 6）",
    "floors_below": "地下階数（数字のみ。例: 1）",
    "height": "建物の高さ（数字のみ、m単位。例: 22.5）",
    "site_area": "敷地面積（数字のみ、㎡単位。例: 500.00）",
    "building_area": "建築面積（数字のみ、㎡単位。例: 350.00）",
    "total_floor_area": "延べ面積（数字のみ、㎡単位。例: 2100.00）",
    "start_date": "着工予定日（例: 令和8年5月1日）",
    "end_date": "完了予定日（例: 令和8年10月31日）",
    "applicant_name": "届出者・建築主の氏名または法人名",
    "applicant_address": "届出者・建築主の住所",
    "applicant_tel": "届出者・建築主の電話番号",
    "designer_name": "設計者名（事務所名 or 個人名）",
    "designer_tel": "設計者の電話番号",
    "constructor_name": "施工者名（建設会社名）",
    "constructor_tel": "施工者の電話番号",
    "site_manager": "現場責任者名",
}

# Geminiへのプロンプト
_SYSTEM_PROMPT = """あなたは建設業の書類読み取りAIです。
アップロードされた書類（建築確認申請書、工事看板の写真、見積書、契約書など）から
工事に関する情報を正確に抽出してください。

以下のJSON形式で出力してください。読み取れない項目は空文字""にしてください。
推測や創作は絶対にしないでください。書類に明記されている情報のみを抽出してください。

出力フォーマット（JSON）:
"""


def _get_api_key():
    """Gemini APIキーを取得（.env / Streamlit secrets / 環境変数）"""
    # 環境変数（.env含む）
    key = os.environ.get("GEMINI_API_KEY", "")
    if key:
        return key

    # Streamlit secrets
    try:
        import streamlit as st
        key = st.secrets.get("GEMINI_API_KEY", "")
        if key:
            return key
    except Exception:
        pass

    return ""


def is_available():
    """OCR機能が利用可能かどうか"""
    return genai is not None and bool(_get_api_key())


def extract_from_file(file_bytes, file_name, mime_type=None):
    """ファイル（PDF/画像）から工事情報を抽出

    Args:
        file_bytes: ファイルのバイト列
        file_name: ファイル名
        mime_type: MIMEタイプ（Noneなら拡張子から推定）

    Returns:
        dict: 抽出された情報（キーはEXTRACT_FIELDSのキー）
        str: 抽出元の生テキスト（デバッグ用）
    """
    if not genai:
        return {}, "google-generativeai パッケージが未インストールです"

    api_key = _get_api_key()
    if not api_key:
        return {}, "GEMINI_API_KEY が設定されていません"

    genai.configure(api_key=api_key)

    # MIMEタイプ推定
    if not mime_type:
        ext = os.path.splitext(file_name)[1].lower()
        mime_map = {
            ".pdf": "application/pdf",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif",
            ".bmp": "image/bmp",
            ".tiff": "image/tiff",
            ".tif": "image/tiff",
        }
        mime_type = mime_map.get(ext, "application/octet-stream")

    # フィールド定義をプロンプトに含める
    fields_json = json.dumps(
        {k: "" for k in EXTRACT_FIELDS},
        ensure_ascii=False,
        indent=2,
    )
    fields_desc = "\n".join(
        [f'  "{k}": {v}' for k, v in EXTRACT_FIELDS.items()]
    )

    prompt = (
        _SYSTEM_PROMPT
        + fields_json
        + "\n\n各フィールドの説明:\n"
        + fields_desc
        + "\n\nこの書類から読み取れる情報をJSON形式で出力してください。JSONのみを出力し、それ以外のテキストは出力しないでください。"
    )

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")

        # Geminiにファイルを送信
        file_part = {
            "mime_type": mime_type,
            "data": file_bytes,
        }
        response = model.generate_content([prompt, file_part])

        raw_text = response.text.strip()

        # JSONを抽出（```json ... ``` で囲まれている場合に対応）
        json_text = raw_text
        if "```json" in json_text:
            json_text = json_text.split("```json")[1].split("```")[0].strip()
        elif "```" in json_text:
            json_text = json_text.split("```")[1].split("```")[0].strip()

        extracted = json.loads(json_text)

        # 定義にないキーを除外
        result = {}
        for key in EXTRACT_FIELDS:
            val = extracted.get(key, "")
            if val and isinstance(val, str):
                result[key] = val.strip()

        return result, raw_text

    except json.JSONDecodeError as e:
        return {}, f"JSON解析エラー: {e}\n\n生のレスポンス:\n{raw_text}"
    except Exception as e:
        return {}, f"Gemini APIエラー: {e}"


# ========== 石綿（アスベスト）事前調査結果からの抽出 ==========

ASBESTOS_FIELDS = {
    "asbestos_present": "石綿含有の有無（有り / 無し / みなし）",
    "asbestos_level": "石綿レベル（レベル1: 吹付け材 / レベル2: 保温材等 / レベル3: 成形板等）",
    "asbestos_locations": "石綿が検出された箇所（例: 外壁サイディング、屋根スレート、天井吹付け材）",
    "asbestos_types": "石綿の種類（例: クリソタイル、アモサイト、クロシドライト）",
    "asbestos_survey_date": "調査日（例: 令和8年2月15日）",
    "asbestos_survey_company": "調査機関名（例: ○○環境分析センター）",
    "asbestos_surveyor": "調査者名",
    "asbestos_removal_method": "除去・処理方法（例: 湿潤化して手作業で除去）",
    "asbestos_area": "石綿使用面積（㎡）",
    "building_construction_year": "建物の竣工年・築年数",
    "building_structure_type": "建物の構造（例: RC造、S造、木造）",
}

_ASBESTOS_SYSTEM_PROMPT = """あなたは石綿（アスベスト）事前調査結果報告書の読み取りAIです。
アップロードされた書類から石綿に関する情報を正確に抽出してください。

以下のJSON形式で出力してください。読み取れない項目は空文字""にしてください。
推測や創作は絶対にしないでください。書類に明記されている情報のみを抽出してください。

出力フォーマット（JSON）:
"""


def extract_asbestos_info(file_bytes, file_name, mime_type=None):
    """石綿事前調査結果報告書から情報を抽出

    Args:
        file_bytes: ファイルのバイト列
        file_name: ファイル名
        mime_type: MIMEタイプ

    Returns:
        dict: 抽出された石綿情報
        str: 生テキスト（デバッグ用）
    """
    if not genai:
        return {}, "google-generativeai パッケージが未インストールです"

    api_key = _get_api_key()
    if not api_key:
        return {}, "GEMINI_API_KEY が設定されていません"

    genai.configure(api_key=api_key)

    if not mime_type:
        ext = os.path.splitext(file_name)[1].lower()
        mime_map = {
            ".pdf": "application/pdf",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
        }
        mime_type = mime_map.get(ext, "application/octet-stream")

    fields_json = json.dumps(
        {k: "" for k in ASBESTOS_FIELDS},
        ensure_ascii=False,
        indent=2,
    )
    fields_desc = "\n".join(
        [f'  "{k}": {v}' for k, v in ASBESTOS_FIELDS.items()]
    )

    prompt = (
        _ASBESTOS_SYSTEM_PROMPT
        + fields_json
        + "\n\n各フィールドの説明:\n"
        + fields_desc
        + "\n\nこの石綿調査報告書から読み取れる情報をJSON形式で出力してください。JSONのみを出力し、それ以外のテキストは出力しないでください。"
    )

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        file_part = {"mime_type": mime_type, "data": file_bytes}
        response = model.generate_content([prompt, file_part])

        raw_text = response.text.strip()

        json_text = raw_text
        if "```json" in json_text:
            json_text = json_text.split("```json")[1].split("```")[0].strip()
        elif "```" in json_text:
            json_text = json_text.split("```")[1].split("```")[0].strip()

        extracted = json.loads(json_text)

        result = {}
        for key in ASBESTOS_FIELDS:
            val = extracted.get(key, "")
            if val and isinstance(val, str):
                result[key] = val.strip()

        return result, raw_text

    except json.JSONDecodeError as e:
        return {}, f"JSON解析エラー: {e}\n\n生のレスポンス:\n{raw_text}"
    except Exception as e:
        return {}, f"Gemini APIエラー: {e}"
