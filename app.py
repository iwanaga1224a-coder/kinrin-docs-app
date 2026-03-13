# -*- coding: utf-8 -*-
"""近隣説明会 書類生成アプリ（Streamlit）

フロー:
  ① 住所を入力 → 区を自動判定・緯度経度を自動取得
  ② 届出ルールを確認（区ごとに異なる範囲・届出先）
  ③ 書類を一括生成（Word 4点セット + 地図）
"""

import os
import io
import sys
import zipfile
import tempfile
import traceback
import streamlit as st

try:
    import folium
    from folium import Circle, Marker, DivIcon
    from streamlit_folium import st_folium

    sys.path.insert(0, os.path.dirname(__file__))
    from geocoder import geocode, extract_ward, extract_ward_with_suffix
    from map_generator import generate_map_png, _calc_zoom, TILE_PROVIDERS
    from nearby_search import search_nearby, format_nearby_list
    from doc_generator import (
        generate_sign_notice,
        generate_explanation_report,
        generate_demolition_report,
        generate_demolition_sign,
        generate_construction_notice,
        generate_map_document,
    )
    from ward_config import get_demolition_checkboxes
except Exception as e:
    st.error(f"起動エラー: {type(e).__name__}: {e}")
    st.code(traceback.format_exc())
    st.stop()

# ========== ページ設定 ==========
st.set_page_config(
    page_title="KINRIN - 近隣説明書類生成",
    page_icon="⛑️",
    layout="wide",
)

# カスタムCSS
st.markdown("""
<style>
/* === 全体テーマ === */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&display=swap');

.stApp {
    font-family: 'Noto Sans JP', sans-serif;
}

/* ヘッダー */
.app-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: white;
    padding: 2rem 2.5rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}
.app-header h1 {
    font-size: 1.8rem;
    font-weight: 700;
    margin: 0 0 0.3rem 0;
    letter-spacing: 0.05em;
}
.app-header .subtitle {
    font-size: 0.95rem;
    color: #94a3b8;
    font-weight: 300;
}
.app-header .badge {
    display: inline-block;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.2);
    color: #e2e8f0;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-size: 0.75rem;
    margin-top: 0.5rem;
    letter-spacing: 0.03em;
}

/* ステップヘッダー */
.step-header {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    margin: 1.5rem 0 0.8rem 0;
}
.step-number {
    background: #0f3460;
    color: white;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 1rem;
    flex-shrink: 0;
}
.step-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1e293b;
}

/* 情報カード */
.info-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    margin: 0.8rem 0;
}
.info-card.detected {
    background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
    border-color: #86efac;
}
.info-card .label {
    font-size: 0.75rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.2rem;
}
.info-card .value {
    font-size: 1.05rem;
    font-weight: 500;
    color: #1e293b;
}

/* サイドバー */
section[data-testid="stSidebar"] {
    background: #f8fafc;
}
section[data-testid="stSidebar"] .stMarkdown h2 {
    font-size: 1.1rem;
    color: #0f3460;
}

/* ボタン */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0f3460, #1a5276) !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em !important;
    padding: 0.7rem 2rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 4px 15px rgba(15,52,96,0.3) !important;
    transform: translateY(-1px) !important;
}

/* タブ */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
    padding: 0.5rem 1.5rem;
    font-weight: 500;
}

/* expander */
.streamlit-expanderHeader {
    font-weight: 500;
    color: #1e293b;
}

/* エラー表示をシンプルに（スタックトレース非表示） */
.stException pre {
    display: none !important;
}
.stException {
    font-size: 0.85rem;
}

/* 免責フッター */
.footer-disclaimer {
    background: #f1f5f9;
    border-radius: 8px;
    padding: 1rem 1.5rem;
    margin-top: 2rem;
    font-size: 0.8rem;
    color: #64748b;
    line-height: 1.7;
}
</style>
""", unsafe_allow_html=True)

# ヘッダー
st.markdown("""
<div class="app-header">
    <div style="font-size:2.5rem; margin-bottom:0.3rem;">⛑️</div>
    <h1>KINRIN</h1>
    <div class="subtitle">近隣説明会 書類生成システム &mdash; 住所入力から届出書類4点セットを一括生成</div>
    <div class="badge">東京23区 + 多摩26市 対応</div>
</div>
""", unsafe_allow_html=True)

# ========== サイドバー ==========
st.sidebar.markdown("""
<div style="text-align:center; padding: 0.5rem 0 1rem 0;">
    <span style="font-size:1.4rem; font-weight:700; color:#0f3460; letter-spacing:0.1em;">KINRIN</span>
    <br>
    <span style="font-size:0.7rem; color:#94a3b8;">近隣説明書類生成システム</span>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.markdown("""
**使い方**

**STEP 1** 住所を入力 → 区を自動判定、工事カテゴリ選択

**STEP 2** 届出ルールを確認

**STEP 3** 工事情報を入力

**STEP 4** 書類を一括生成・ダウンロード
""")
st.sidebar.markdown("---")
st.sidebar.markdown("""
**生成される書類**
- 近隣説明範囲図（地図付き）
- 標識設置届（新築） / 事前周知報告書（解体）
- 近隣説明報告書（新築のみ）
- 工事のお知らせ
""")
st.sidebar.markdown("---")
st.sidebar.caption("届出前に必ず管轄窓口で内容をご確認ください。生成結果の正確性は保証されません。")

# ========== STEP 1：住所入力 ==========
st.markdown('<div class="step-header"><div class="step-number">1</div><div class="step-title">工事場所</div></div>', unsafe_allow_html=True)

# --- 書類アップロードによる自動入力 ---
from ocr_extractor import is_available as ocr_available, extract_from_file, extract_asbestos_info, EXTRACT_FIELDS, ASBESTOS_FIELDS

with st.expander("📄 書類をアップロードして自動入力", expanded=False):
    st.caption(
        "現場書類・石綿調査報告書・工事看板の写真などをアップロードすると、"
        "現場情報と石綿情報をまとめて読み取りフォームに自動入力します。"
    )
    if not ocr_available():
        st.warning("⚠️ Gemini APIキーが設定されていないため、この機能は利用できません。")
    else:
        uploaded_files = st.file_uploader(
            "PDF・画像ファイルをアップロード（複数可）",
            type=["pdf", "png", "jpg", "jpeg", "webp", "bmp", "tiff"],
            key="ocr_upload",
            accept_multiple_files=True,
        )
        if uploaded_files:
            if st.button("📖 読み取り開始", type="primary"):
                total_filled = 0
                all_details = {}
                for uf in uploaded_files:
                    file_bytes = uf.read()
                    # 現場情報の読み取り
                    with st.spinner(f"{uf.name} から現場情報を読み取り中..."):
                        extracted, raw = extract_from_file(file_bytes, uf.name, uf.type)
                    if extracted:
                        for key, val in extracted.items():
                            if val:
                                st.session_state[f"_ocr_{key}"] = val
                                all_details[EXTRACT_FIELDS.get(key, key)] = val
                                total_filled += 1
                    # 石綿情報の読み取り（同じファイルから）
                    with st.spinner(f"{uf.name} から石綿情報を読み取り中..."):
                        asb_result, asb_raw = extract_asbestos_info(file_bytes, uf.name, uf.type)
                    if asb_result:
                        _asb_map = {
                            "asbestos_level": "_asb_level",
                            "asbestos_locations": "_asb_locations",
                            "asbestos_types": "_asb_types",
                            "asbestos_survey_date": "_asb_survey_date",
                            "asbestos_survey_company": "_asb_survey_company",
                            "asbestos_surveyor": "_asb_surveyor",
                            "asbestos_removal_method": "_asb_removal_method",
                            "asbestos_area": "_asb_area",
                            "building_construction_year": "_asb_construction_year",
                        }
                        for src_key, dst_key in _asb_map.items():
                            if asb_result.get(src_key):
                                st.session_state[dst_key] = asb_result[src_key]
                                all_details[ASBESTOS_FIELDS.get(src_key, src_key)] = asb_result[src_key]
                                total_filled += 1
                        if asb_result.get("asbestos_present"):
                            st.session_state["_asb_present"] = asb_result["asbestos_present"]
                if total_filled > 0:
                    st.success(f"✅ {total_filled} 項目を読み取りました！下のフォームに自動入力されています。")
                    with st.expander("読み取り結果の詳細", expanded=False):
                        for label, val in all_details.items():
                            st.markdown(f"- **{label}**: {val}")
                    st.rerun()
                else:
                    st.error("読み取れませんでした。手動で入力してください。")

def _ocr_val(field_id, fallback=""):
    """OCRで読み取った値があればそれを返す（手動入力で上書き可）"""
    return st.session_state.get(f"_ocr_{field_id}", fallback)

site_address = st.text_input(
    "工事場所（住所） *",
    value=_ocr_val("site_address"),
    placeholder="東京都新宿区西新宿2-8-1",
)

project_category = st.radio(
    "工事カテゴリ",
    ["新築・増築", "解体"],
    horizontal=True,
    help="解体工事の場合、標識設置届・設計者欄など不要な項目を自動的にスキップします",
)
is_demolition = (project_category == "解体")

# 住所から自動判定
detected_ward = ""
detected_coords = None
if site_address:
    detected_ward = extract_ward(site_address)
    detected_ward_full = extract_ward_with_suffix(site_address)
    detected_coords = geocode(site_address)

    if detected_ward:
        from ward_config import get_ward_config
        wc = get_ward_config(detected_ward)

        if is_demolition:
            # === 解体モード: 解体専用の情報を表示 ===
            _demo_cfg = wc.get("demolition", {})
            _demo_ordinance = _demo_cfg.get("ordinance_name", "解体工事に関する要綱")
            st.markdown(f"""
            <div class="info-card detected">
                <div class="label">届出先（自動判定）</div>
                <div class="value">{detected_ward_full}</div>
                <div style="font-size:0.85rem; color:#475569; margin-top:0.3rem;">{_demo_ordinance}</div>
            </div>
            """, unsafe_allow_html=True)

            _deadline_w = _demo_cfg.get("sign_deadline_wood", "要確認")
            _deadline_o = _demo_cfg.get("sign_deadline_other", "要確認")
            _target = _demo_cfg.get("target_area", 80)
            _note = _demo_cfg.get("form_note", "")
            _target_str = "全ての建物" if _target == 0 else f"延べ面積{_target}m²以上"
            _scope = _demo_cfg.get("scope_rule", "")
            _large = _demo_cfg.get("large_building_criteria", "")
            _submit_to = _demo_cfg.get("submit_to", "")

            req_cols = st.columns(3)
            with req_cols[0]:
                st.markdown(f"**対象:** {_target_str}")
            with req_cols[1]:
                st.markdown(f"**掲示期限:** 小規模 **{_deadline_w}日前** ／ 大規模 **{_deadline_o}日前**")
            with req_cols[2]:
                if _submit_to:
                    st.markdown(f"**届出先:** {_submit_to}")

            if _large:
                st.warning(f"規模による（{_large}）")
            st.caption("⚠️ 解体工事のお知らせ標識・報告書は本アプリで生成可能です。印刷時にA3以上に拡大してください。")
        else:
            # === 新築・増築モード: 中高層条例の情報を表示 ===
            st.markdown(f"""
            <div class="info-card detected">
                <div class="label">届出先（自動判定）</div>
                <div class="value">{detected_ward_full}</div>
                <div style="font-size:0.85rem; color:#475569; margin-top:0.3rem;">{wc['ordinance_name']}</div>
            </div>
            """, unsafe_allow_html=True)

            req_cols = st.columns(3)
            with req_cols[0]:
                st.markdown(f"**標識設置根拠:** {wc['sign_article']}")
            with req_cols[1]:
                st.markdown(f"**説明義務根拠:** {wc['explanation_article']}")
            with req_cols[2]:
                if wc.get("height_threshold"):
                    st.markdown(f"**対象:** {wc['height_threshold']}")
            if wc.get("sign_period"):
                st.warning(f"標識届出期限: {wc['sign_period']}")
            if wc.get("note"):
                st.info(f"{detected_ward_full}の注意点: {wc['note']}")
            if wc.get("uses_metro_ordinance"):
                st.warning("この区は独自条例がなく、東京都条例が適用されます。届出先は東京都になる場合があります。")

        # 公式テンプレート利用状況
        from template_filler import get_available_templates, get_available_demolition_templates
        if is_demolition:
            demo_tpl = get_available_demolition_templates(detected_ward)
            if demo_tpl.get("sign") or demo_tpl.get("report"):
                _tpl_types = []
                if demo_tpl.get("sign"):
                    _tpl_types.append("標識")
                if demo_tpl.get("report"):
                    _tpl_types.append("報告書")
                st.caption(f"様式: {detected_ward_full}の解体工事用**公式様式**を使用（{'・'.join(_tpl_types)}）")
            else:
                st.caption(f"様式: {detected_ward_full}は解体用の汎用フォーマットで生成します（公式様式は未対応）")
        else:
            tpl_avail = get_available_templates(detected_ward)
            if tpl_avail["sign_notice"]:
                st.caption(f"様式: {detected_ward_full}の公式様式を使用（{tpl_avail['sign_notice'].upper()}形式）")
            else:
                st.caption(f"様式: {detected_ward_full}は汎用フォーマットで生成します")
    else:
        st.warning("区名を判定できませんでした。手動で入力してください。")
    if not detected_coords:
        st.warning("住所から位置を取得できませんでした。住所を確認してください。")

# ========== STEP 2：届出ルール ==========
st.markdown('<div class="step-header"><div class="step-number">2</div><div class="step-title">届出ルールの確認</div></div>', unsafe_allow_html=True)

if is_demolition:
    st.info(
        "解体工事の事前周知の範囲・届出先は**自治体ごとに異なります**。\n\n"
        "- 独自の解体事前周知要綱がある区（23区はほぼ全区）\n"
        "- 建設リサイクル法の届出のみの市（多摩地域の多く）\n"
        "- 延べ面積80m²以上で届出が必要な区が多い\n\n"
        "各自治体の建築課・環境対策課等の窓口で最新のルール・ひな形をご確認ください。\n"
        "ここでは範囲を手動で設定できます。"
    )
else:
    st.info(
        "近隣説明の範囲・届出先の部署は**区ごとに異なります**。\n\n"
        "- 半径○mの円で指定する区\n"
        "- 建物高さを敷地境界から倒した範囲で指定する区\n"
        "- 高さ10m超で中高層条例が適用される区\n\n"
        "各区の建築課・環境対策課等の窓口で最新のルール・ひな形をご確認ください。\n"
        "ここでは範囲を手動で設定できます。"
    )

# 区別の参照URL表示（工事種別に応じて切替）
if detected_ward:
    from ward_config import get_ward_config as _gwc
    _wc_for_url = _gwc(detected_ward)
    detected_ward_suffix = detected_ward_full if "detected_ward_full" in dir() else detected_ward
    if is_demolition and _wc_for_url.get("demolition_url"):
        st.markdown(
            f"📎 **{detected_ward_suffix}の解体工事 事前周知・届出ページ**: "
            f"[{_wc_for_url['demolition_url']}]({_wc_for_url['demolition_url']})"
        )
        st.caption("※ URLは変更される場合があります。リンク切れの際は「○○区 解体工事 事前周知 届出」等で検索してください。")
    elif is_demolition and not _wc_for_url.get("demolition_url"):
        st.info(f"ℹ️ {detected_ward_suffix}には独自の解体事前周知制度がありません。建設リサイクル法に基づく届出は東京都多摩建築指導事務所が管轄です。")
    elif not is_demolition and _wc_for_url.get("regulation_url"):
        st.markdown(
            f"📎 **{detected_ward_suffix}の中高層条例・届出様式ページ**: "
            f"[{_wc_for_url['regulation_url']}]({_wc_for_url['regulation_url']})"
        )
        st.caption("※ URLは変更される場合があります。リンク切れの際は「○○区 中高層 標識設置届」等で検索してください。")

# --- 手続きガイド ---
if detected_ward:
    from ward_config import get_procedure_guide
    _guide = get_procedure_guide(detected_ward)
    _ward_sfx = detected_ward_full if "detected_ward_full" in dir() else detected_ward

    _display_url = _wc_for_url.get("demolition_url", "") if is_demolition else _guide.get("regulation_url", "")
    _expander_title = f"📋 {_ward_sfx} 手続きガイド — {'解体工事の届出' if is_demolition else '必要な書類・手続きの流れ'}"
    with st.expander(_expander_title, expanded=False):
        if is_demolition:
            # === 解体モード用の手続きガイド ===
            _demo_cfg = _wc_for_url.get("demolition", {})
            st.markdown("### 解体工事の手続きの流れ")
            _demo_steps = [
                ("対象確認", f"解体工事が事前周知の対象か確認（{_demo_cfg.get('form_note', '各区の要綱を確認')}）"),
                ("標識（看板）の設置", "解体工事のお知らせ看板を現場に設置（区の公式様式を使用）"),
                ("近隣住民への事前周知", "説明範囲内の住民に個別訪問・説明会・書面配付等で周知"),
                ("事前周知報告書の提出", f"{_ward_sfx}に報告書を提出（案内図・チラシ等を添付）"),
                ("建設リサイクル法届出", "延べ面積80m²以上の場合、着手7日前までに届出"),
                ("解体工事着手", "上記手続き完了後、工事着手"),
            ]
            for i, (title, detail) in enumerate(_demo_steps, 1):
                st.markdown(f"**{i}. {title}**  \n{detail}")

            st.markdown("---")

            st.markdown("### 必要書類・準備物")
            _demo_docs = [
                ("✅", "【必須】", "事前周知報告書", "本アプリで生成可能"),
                ("✅", "【必須】", "解体工事のお知らせ標識", "本アプリで生成可能（A3以上に拡大して掲示）"),
                ("✅", "【必須】", "近隣説明範囲図（案内図）", "本アプリで生成可能"),
                ("✅", "【必須】", "工事のお知らせ（近隣配布チラシ）", "本アプリで生成可能"),
                ("📎", "【任意】", "工事対象建物の写真", "遠景・近景（添付推奨）"),
                ("📎", "【該当時】", "建設リサイクル法届出書", "延べ80m²以上の場合（別途作成）"),
            ]
            for icon, req, name, how in _demo_docs:
                st.markdown(f"{icon} {req} **{name}**  \n　{how}")
        else:
            # === 新築モード用の手続きガイド ===
            st.markdown("### 手続きの流れ")
            for step in _guide["steps"]:
                st.markdown(f"**{step['order']}. {step['title']}**  \n{step['detail']}")

            st.markdown("---")

            st.markdown("### 必要書類・準備物")
            for doc in _guide["documents"]:
                icon = "✅" if doc["required"] else "📎"
                req_label = "【必須】" if doc["required"] else "【任意】"
                st.markdown(f"{icon} {req_label} **{doc['name']}**  \n　{doc['how']}")

        st.markdown("---")

        # 標識（看板）の設置要件（共通）
        st.markdown(f"### {'解体工事お知らせ看板' if is_demolition else '標識（看板）'}の設置要件")
        sr = _guide["sign_requirements"]
        st.markdown(f"- **設置場所**: {sr['location']}")
        st.markdown(f"- **設置時期**: {sr['timing']}")
        if not is_demolition:
            st.markdown(f"- **記載事項**: {sr['content']}")
        st.info(f"💡 {sr['note']}")
        if is_demolition:
            st.caption("✅ 解体工事のお知らせ標識は本アプリで生成できます。A3以上に拡大して掲示してください。")
        else:
            st.caption("⚠️ 看板の実物（現場掲示用）はこのツールでは生成しません。公式サイトから様式をダウンロードして作成してください。")
        if _display_url:
            st.caption(f"　→ 公式ページ: {_display_url}")

        st.markdown("---")

        # 注意点
        if _guide["tips"]:
            st.markdown(f"### {'この自治体' if is_demolition else 'この区'}の注意点")
            for tip in _guide["tips"]:
                st.warning(tip)

        # 参考URL
        if _display_url:
            st.markdown(f"🔗 **公式ページ**: [{_display_url}]({_display_url})")

        # メモ帳出力ボタン
        _memo_lines = []
        _memo_lines.append(f"========================================")
        _memo_lines.append(f"  {_ward_sfx} 近隣説明 手続きガイド")
        _memo_lines.append(f"========================================")
        _memo_lines.append("")
        _memo_lines.append("【手続きの流れ】")
        for step in _guide["steps"]:
            _memo_lines.append(f"  {step['order']}. {step['title']}")
            _memo_lines.append(f"     → {step['detail']}")
        _memo_lines.append("")
        _memo_lines.append("【必要書類・準備物】")
        for doc in _guide["documents"]:
            req = "必須" if doc["required"] else "任意"
            _memo_lines.append(f"  [{req}] {doc['name']}")
            _memo_lines.append(f"         {doc['how']}")
        _memo_lines.append("")
        _memo_lines.append("【標識（看板）の設置要件】")
        _memo_lines.append(f"  設置場所: {sr['location']}")
        _memo_lines.append(f"  設置時期: {sr['timing']}")
        _memo_lines.append(f"  記載事項: {sr['content']}")
        _memo_lines.append(f"  ※ {sr['note']}")
        _memo_lines.append("")
        _memo_lines.append("【注意点】")
        for tip in _guide["tips"]:
            _memo_lines.append(f"  ・{tip}")
        if _display_url:
            _memo_lines.append("")
            _memo_lines.append(f"【参考URL】")
            _memo_lines.append(f"  {_display_url}")
        _memo_lines.append("")
        _memo_lines.append("※ 本ガイドはAIが条例情報から自動生成した参考情報です。")
        _memo_lines.append("  届出前に必ず管轄窓口で最新の様式・要件をご確認ください。")
        _memo_text = "\n".join(_memo_lines)

        st.download_button(
            label="📝 手続きガイドをメモ帳で保存",
            data=_memo_text.encode("utf-8"),
            file_name=f"手続きガイド_{_ward_sfx}.txt",
            mime="text/plain",
        )

st.markdown('<div class="step-header"><div class="step-number" style="background:#e65100;">⚙</div><div class="step-title">近隣説明範囲の設定</div></div>', unsafe_allow_html=True)

col_rule1, col_rule2, col_rule3 = st.columns(3)
with col_rule1:
    range_type = st.selectbox("説明範囲の種類", [
        "敷地境界から10mの範囲",
        "建物の高さ分の範囲",
        "半径○mの円",
    ])
with col_rule2:
    if range_type == "敷地境界から10mの範囲":
        radius_m = 10
        st.caption("敷地境界から10mの範囲を円で概算表示します。\n正確な範囲は敷地図に基づいて作成してください。")
    elif range_type == "建物の高さ分の範囲":
        building_height_for_range = st.number_input(
            "建物の高さ（m）", min_value=1.0, max_value=200.0, value=20.0, step=0.5,
            help="この高さを敷地境界からの説明範囲として使用します"
        )
        radius_m = int(building_height_for_range)
        st.caption(f"建物高さ {building_height_for_range}m を概算の円（半径{radius_m}m）で表示します。\n正確な範囲は敷地図に基づいて作成してください。")
    else:
        radius_m = st.slider("説明範囲（半径m）", min_value=10, max_value=200, value=50, step=10)
with col_rule3:
    ward_name_input = st.text_input("届出先の区名（自動判定を修正する場合）", value=detected_ward)

# おすすめ範囲の注釈
if detected_ward:
    _wc_range = get_ward_config(detected_ward)
    _ht = _wc_range.get("height_threshold", "")
    if is_demolition:
        _demo_cfg = _wc_range.get("demolition", {})
        _target = _demo_cfg.get("target_area", 80)
        _target_str = "全ての建物" if _target == 0 else f"延べ面積{_target}m²以上"
        st.info(
            f"**💡 {detected_ward}の解体工事 — おすすめ設定**\n\n"
            f"- 対象: {_target_str}\n"
            f"- 多くの区では **「建物の高さ分の範囲」** または **「敷地境界から10m」** のどちらか広い方を採用しています\n"
            f"- 建物高さが10mを超えている場合は「建物の高さ分の範囲」を選択してください"
        )
    else:
        st.info(
            f"**💡 {detected_ward}の新築・増築 — おすすめ設定**\n\n"
            f"- 対象: {_ht}\n"
            f"- 多くの区では **「建物の高さ分の範囲」** が説明範囲の基準です（敷地境界から建物高さの距離）\n"
            f"- 建物高さが10m以下なら「敷地境界から10mの範囲」で十分な場合が多いです"
        )

# ========== 地図プレビュー ==========
if detected_coords:
    st.subheader("地図プレビュー")
    st.caption("拡大・縮小・移動で調整してください。この表示範囲が書類の地図に反映されます。")

    col_map_opt1, col_map_opt2 = st.columns([2, 1])
    with col_map_opt1:
        tile_choice = st.radio("地図の種類", list(TILE_PROVIDERS.keys()), horizontal=True, index=0)
    with col_map_opt2:
        zoom_adjust = st.slider("拡大・縮小", min_value=-3, max_value=5, value=0, step=1,
                                help="＋で拡大、−で縮小。0が自動。国土地理院はzoom18以上も拡大可")

    # 地図操作モード
    map_mode = st.radio(
        "地図クリック操作",
        ["操作なし", "建物番号を配置", "看板設置箇所を配置", "位置を移動"],
        horizontal=True,
        help="モードを選んで地図をクリックしてください",
    )

    # マーカー位置の管理（住所変更時は座標をリセット）
    prev_addr = st.session_state.get("_last_geocoded_address", "")
    if prev_addr != site_address or "marker_lat" not in st.session_state:
        st.session_state["marker_lat"] = detected_coords[0]
        st.session_state["marker_lng"] = detected_coords[1]
        st.session_state["_last_geocoded_address"] = site_address

    # 手動番号リストの管理
    if "building_pins" not in st.session_state:
        st.session_state["building_pins"] = []
    if "sign_pins" not in st.session_state:
        st.session_state["sign_pins"] = []

    preview_lat = st.session_state["marker_lat"]
    preview_lng = st.session_state["marker_lng"]
    # 配置・移動モード中のみ前回ズームを維持（それ以外は自動計算）
    if map_mode in ("建物番号を配置", "看板設置箇所を配置", "位置を移動") and st.session_state.get("_map_zoom"):
        preview_zoom = st.session_state["_map_zoom"]
    else:
        preview_zoom = _calc_zoom(radius_m, zoom_offset=zoom_adjust)

    if map_mode == "建物番号を配置":
        st.info("地図をクリック → その位置に番号ピンを追加します")
    elif map_mode == "看板設置箇所を配置":
        st.info("地図をクリック → 看板設置箇所（●）を配置します。複数配置可。")

    tile_info = TILE_PROVIDERS[tile_choice]
    max_zoom = tile_info.get("max_zoom", 21)
    preview_map = folium.Map(
        location=[preview_lat, preview_lng],
        zoom_start=preview_zoom,
        tiles=None,
        max_zoom=max_zoom,
    )
    if tile_info["attr"]:
        folium.TileLayer(
            tiles=tile_info["tiles"],
            attr=tile_info["attr"],
            max_native_zoom=tile_info.get("max_native_zoom", 18),
            max_zoom=max_zoom,
        ).add_to(preview_map)
    else:
        folium.TileLayer(
            tiles=tile_info["tiles"],
            max_native_zoom=tile_info.get("max_native_zoom", 19),
            max_zoom=max_zoom,
        ).add_to(preview_map)

    # 近隣説明範囲（赤い円）
    Circle(
        location=[preview_lat, preview_lng],
        radius=radius_m,
        color="red",
        weight=3,
        fill=True,
        fill_color="red",
        fill_opacity=0.08,
    ).add_to(preview_map)

    # 現場マーカー
    Marker(
        location=[preview_lat, preview_lng],
        popup=f"{st.session_state.get('_site_name_val', '工事現場')}<br>{site_address}",
        icon=DivIcon(
            html='<div style="font-size:28px;color:red;text-shadow:1px 1px 2px rgba(0,0,0,0.5);transform:translate(-14px,-14px);">&#9733;</div>',
            icon_size=(30, 30),
            icon_anchor=(0, 0),
        ),
    ).add_to(preview_map)

    # 手動配置済みの番号ピンを地図に表示
    for pin in st.session_state["building_pins"]:
        no = pin["no"]
        Marker(
            location=[pin["lat"], pin["lng"]],
            icon=DivIcon(
                html=f'<div style="'
                     f'font-size:16px;font-weight:bold;color:white;'
                     f'background:#1a73e8;border:3px solid white;'
                     f'border-radius:50%;width:32px;height:32px;'
                     f'display:flex;align-items:center;justify-content:center;'
                     f'box-shadow:1px 1px 4px rgba(0,0,0,0.5);'
                     f'transform:translate(-16px,-16px);'
                     f'">{no}</div>',
                icon_size=(32, 32),
                icon_anchor=(0, 0),
            ),
        ).add_to(preview_map)

    # 看板設置箇所ピンを地図に表示
    for si, spin in enumerate(st.session_state["sign_pins"]):
        Marker(
            location=[spin["lat"], spin["lng"]],
            popup="看板設置箇所",
            icon=DivIcon(
                html='<div style="'
                     'font-size:20px;font-weight:bold;color:#e65100;'
                     'background:white;border:3px solid #e65100;'
                     'border-radius:50%;width:32px;height:32px;'
                     'display:flex;align-items:center;justify-content:center;'
                     'box-shadow:1px 1px 4px rgba(0,0,0,0.5);'
                     'transform:translate(-16px,-16px);'
                     '">●</div>',
                icon_size=(32, 32),
                icon_anchor=(0, 0),
            ),
        ).add_to(preview_map)

    # インタラクティブ地図を表示
    map_output = st_folium(preview_map, width=800, height=500)

    # ズームレベルを保存（リロード後も維持）
    if map_output and map_output.get("zoom"):
        st.session_state["_map_zoom"] = map_output["zoom"]

    # 移動モード：地図の下に対象選択を表示
    if map_mode == "位置を移動":
        _pins = st.session_state.get("building_pins", [])
        _spins = st.session_state.get("sign_pins", [])
        _move_options = ["★（工事現場）"] + [f"{p['no']}番 {p.get('label','') or '建物'}" for p in _pins] + [f"●看板{i+1}" for i in range(len(_spins))]
        _move_sel = st.selectbox("移動する対象を選択", _move_options, key="_pin_move_sel")
        st.session_state["_move_target"] = _move_sel
        st.caption(f"📍 {_move_sel} を選択中 — 地図をクリックでその位置に移動")

    # クリック処理（前回と同じクリックは無視）
    if map_output and map_output.get("last_clicked"):
        clicked = map_output["last_clicked"]
        new_lat = round(clicked["lat"], 8)
        new_lng = round(clicked["lng"], 8)
        _click_key = f"{new_lat},{new_lng}"
        _is_new_click = (_click_key != st.session_state.get("_last_click_key"))
        if _is_new_click:
            st.session_state["_last_click_key"] = _click_key

        if not _is_new_click:
            pass  # 同じクリックは無視
        elif map_mode == "建物番号を配置":
            # 既存ピンと近すぎないかチェック（重複防止）
            too_close = False
            for pin in st.session_state["building_pins"]:
                if abs(pin["lat"] - new_lat) < 0.00003 and abs(pin["lng"] - new_lng) < 0.00003:
                    too_close = True
                    break
            if not too_close:
                next_no = len(st.session_state["building_pins"]) + 1
                st.session_state["building_pins"].append({
                    "no": next_no,
                    "lat": new_lat,
                    "lng": new_lng,
                    "label": "",
                })
                st.rerun()

        elif map_mode == "看板設置箇所を配置":
            if len(st.session_state["sign_pins"]) >= 4:
                st.warning("看板設置箇所は最大4箇所までです。")
            else:
                too_close = False
                for spin in st.session_state["sign_pins"]:
                    if abs(spin["lat"] - new_lat) < 0.00003 and abs(spin["lng"] - new_lng) < 0.00003:
                        too_close = True
                        break
                if not too_close:
                    st.session_state["sign_pins"].append({
                        "lat": new_lat,
                        "lng": new_lng,
                    })
                    st.rerun()

        elif map_mode == "位置を移動":
            _target = st.session_state.get("_move_target", "")
            if _target == "★（工事現場）":
                cur_lat = round(st.session_state["marker_lat"], 8)
                cur_lng = round(st.session_state["marker_lng"], 8)
                if new_lat != cur_lat or new_lng != cur_lng:
                    st.session_state["marker_lat"] = new_lat
                    st.session_state["marker_lng"] = new_lng
                    st.rerun()
            elif _target.startswith("●看板"):
                # "●看板N" → インデックス特定
                try:
                    _si = int(_target.replace("●看板", "")) - 1
                    _spins = st.session_state["sign_pins"]
                    if 0 <= _si < len(_spins):
                        if abs(_spins[_si]["lat"] - new_lat) > 0.00001 or abs(_spins[_si]["lng"] - new_lng) > 0.00001:
                            _spins[_si]["lat"] = new_lat
                            _spins[_si]["lng"] = new_lng
                            st.rerun()
                except (ValueError, IndexError):
                    pass
            else:
                # "N番 ラベル" → N を取り出してインデックス特定
                _pins = st.session_state["building_pins"]
                try:
                    _target_no = int(_target.split("番")[0])
                    for _pi, _pp in enumerate(_pins):
                        if _pp["no"] == _target_no:
                            if abs(_pp["lat"] - new_lat) > 0.00001 or abs(_pp["lng"] - new_lng) > 0.00001:
                                _pins[_pi]["lat"] = new_lat
                                _pins[_pi]["lng"] = new_lng
                                st.rerun()
                            break
                except (ValueError, IndexError):
                    pass

    # 番号ピン一覧と編集
    if st.session_state["building_pins"]:
        st.subheader(f"配置済み建物（{len(st.session_state['building_pins'])}件）")
        for i, pin in enumerate(st.session_state["building_pins"]):
            col_no, col_label, col_del = st.columns([1, 6, 1])
            with col_no:
                st.markdown(f"**{pin['no']}**")
            with col_label:
                new_label = st.text_input(
                    f"物件{pin['no']}の説明",
                    value=pin.get("label", ""),
                    key=f"pin_label_{i}",
                    placeholder="例: 戸建て住宅、集合住宅、○○医院 など",
                    label_visibility="collapsed",
                )
                if new_label != pin.get("label", ""):
                    st.session_state["building_pins"][i]["label"] = new_label
            with col_del:
                if st.button("✕", key=f"pin_del_{i}"):
                    st.session_state["building_pins"].pop(i)
                    # 番号を振り直す
                    for j, p in enumerate(st.session_state["building_pins"]):
                        p["no"] = j + 1
                    st.rerun()

        if st.button("全ピンをクリア"):
            st.session_state["building_pins"] = []
            st.rerun()

    # 看板設置箇所の一覧
    if st.session_state["sign_pins"]:
        st.subheader(f"看板設置箇所（{len(st.session_state['sign_pins'])}箇所）")
        st.caption("※ 近隣周知図に●で表示されます。看板の実物は各区の公式様式をご利用ください。")
        for si, spin in enumerate(st.session_state["sign_pins"]):
            col_s_no, col_s_del = st.columns([6, 1])
            with col_s_no:
                st.markdown(f"●看板{si+1}")
            with col_s_del:
                if st.button("✕", key=f"sign_del_{si}"):
                    st.session_state["sign_pins"].pop(si)
                    st.rerun()
        if st.button("全看板ピンをクリア"):
            st.session_state["sign_pins"] = []
            st.rerun()

# ========== STEP 3：工事情報入力 ==========
st.markdown('<div class="step-header"><div class="step-number">3</div><div class="step-title">工事情報の入力</div></div>', unsafe_allow_html=True)
st.caption("以下の入力項目が届出書類に反映されます。")

# 区ごとの必要フィールドを取得
_req_fields = set()
_rf_sign = set()
_rf_report = set()
if detected_ward:
    from template_filler import get_required_fields, FIELD_LABELS
    _rf = get_required_fields(detected_ward)
    _rf_sign = _rf["sign_notice"]
    _rf_report = _rf["report"]
    _req_fields = _rf_sign | _rf_report

def _field_help(field_id):
    """フィールドがどの書類で必要かをhelpテキストとして返す"""
    if not detected_ward:
        return None
    uses = []
    if field_id in _rf_sign and not is_demolition:
        uses.append("標識設置届")
    if field_id in _rf_report:
        uses.append("説明報告書")
    if uses:
        return f"📋 {' / '.join(uses)} で使用"
    if is_demolition and field_id in _rf_sign and field_id not in _rf_report:
        return "解体工事では不要（標識設置届をスキップ）"
    return "この区の様式では不要（空欄でOK）"

# 区の様式でのみ使われるフィールド（該当しなければ非表示）
_CONDITIONAL_FIELDS = {
    "land_number", "zoning", "fire_zone", "other_zone",
    "construction_type", "foundation",
    "unit_count", "oneroom_count",
}

_DEMOLITION_HIDE = {"foundation", "unit_count", "oneroom_count", "construction_type"}

def _show(field_id):
    """区のテンプレートで使うフィールドかどうか"""
    if is_demolition and field_id in _DEMOLITION_HIDE:
        return False  # 解体時は不要
    if not detected_ward:
        return True  # 区未判定時は全表示
    if field_id not in _CONDITIONAL_FIELDS:
        return True  # 常設フィールド
    return field_id in _req_fields

# 非表示フィールドのデフォルト値
construction_type = "解体" if is_demolition else "新築"
foundation = "杭基礎"
land_number = ""
zoning = ""
fire_zone = ""
other_zone = ""
unit_count = ""
oneroom_count = ""

tab1, tab2, tab3, tab4 = st.tabs([
    "建物・工事内容",
    "工期・関係者",
    "説明実施情報",
    "届出・その他",
])

# 届出期限の逆算ヘルパー
def _calc_deadline_info(start_date_str, ward_name):
    """着工日と区名から届出期限の注釈テキストを生成"""
    if not start_date_str or not ward_name:
        return None
    _wc_dl = get_ward_config(ward_name) if ward_name else None
    if not _wc_dl:
        return None
    _sp = _wc_dl.get("sign_period", "")
    if not _sp:
        return None
    import re as _re
    _reiwa_m = _re.match(r"令和(\d+)年(\d+)月(\d+)日", start_date_str)
    if not _reiwa_m:
        return None
    from datetime import date, timedelta
    try:
        _start_dt = date(int(_reiwa_m.group(1)) + 2018, int(_reiwa_m.group(2)), int(_reiwa_m.group(3)))
    except ValueError:
        return None
    _days_list = sorted(set(int(x) for x in _re.findall(r"(\d+)日前", _sp)), reverse=True)
    if not _days_list:
        return None
    lines = []
    for _days in _days_list:
        _dl = _start_dt - timedelta(days=_days)
        _dl_reiwa = f"令和{_dl.year - 2018}年{_dl.month}月{_dl.day}日"
        lines.append(f"**{_days}日前** → {_dl_reiwa}")
    return {
        "lines": lines,
        "note": _sp,
        "start_date": start_date_str,
        "ward": ward_name,
    }

with tab1:
    site_name = st.text_input("工事名称 *", value=_ocr_val("site_name"), placeholder="○○ビル解体工事", key="_site_name_val")
    col1, col2 = st.columns(2)
    with col1:
        building_name = st.text_input("建物名称", value=_ocr_val("building_name"), placeholder="○○ビル", help=_field_help("building_name"))
        building_use = st.text_input(
            "主要用途" if not is_demolition else "既存建物の用途",
            value=_ocr_val("building_use"), placeholder="事務所", help=_field_help("building_use"),
        )
        work_content = st.text_input(
            "工事内容",
            value=_ocr_val("work_content"),
            placeholder="RC造建物の解体工事" if is_demolition else "鉄筋コンクリート造建物の新築工事",
            help=_field_help("work_content"),
        )
        if _show("construction_type") or is_demolition:
            _ct_options = ["解体"] if is_demolition else ["新築", "増築", "改築", "移転", "大規模の修繕", "大規模の模様替", "用途変更", "その他"]
            construction_type = st.selectbox(
                "工事種別",
                _ct_options,
                disabled=is_demolition,
            )
    with col2:
        structure = st.selectbox(
            "構造",
            ["鉄筋コンクリート造", "鉄骨造", "鉄骨鉄筋コンクリート造", "木造", "その他"],
            help=_field_help("structure"),
        )
        if _show("foundation"):
            foundation = st.selectbox(
                "基礎工法",
                ["杭基礎", "直接基礎（べた基礎）", "直接基礎（独立基礎）", "直接基礎（布基礎）", "その他"],
            )
        floors_above = st.text_input("地上階数", value=_ocr_val("floors_above"), placeholder="6", help=_field_help("floors_above"))
        floors_below = st.text_input("地下階数", value=_ocr_val("floors_below"), placeholder="1", help=_field_help("floors_below"))

    col3, col4, col5, col6 = st.columns(4)
    with col3:
        height = st.text_input("高さ（m）", value=_ocr_val("height"), placeholder="22.5", help=_field_help("height"))
    with col4:
        site_area = st.text_input("敷地面積（㎡）", value=_ocr_val("site_area"), placeholder="500.00", help=_field_help("site_area"))
    with col5:
        building_area = st.text_input("建築面積（㎡）", value=_ocr_val("building_area"), placeholder="350.00", help=_field_help("building_area"))
    with col6:
        total_floor_area = st.text_input("延べ面積（㎡）", value=_ocr_val("total_floor_area"), placeholder="2,100.00", help=_field_help("total_floor_area"))

    # 敷地情報（区の様式で必要な場合のみ表示）
    _show_land = _show("land_number") or _show("zoning") or _show("fire_zone") or _show("other_zone")
    if _show_land:
        st.markdown("**敷地情報**")
        col_land1, col_land2 = st.columns(2)
        with col_land1:
            if _show("land_number"):
                land_number = st.text_input("地名地番", placeholder="新宿区西新宿二丁目8番1号")
            if _show("zoning"):
                zoning = st.text_input("用途地域", placeholder="商業地域")
        with col_land2:
            if _show("fire_zone"):
                fire_zone = st.text_input("防火地域", placeholder="防火地域")
            if _show("other_zone"):
                other_zone = st.text_input("その他の地域・地区", placeholder="第3種高度地区")

    # 解体工事専用フィールド（解体モード時のみ表示）
    # チェックボックス用の変数を初期化
    large_building_checks = []
    explanation_method_checks = []
    attachment_checks = []
    specific_construction_status = ""
    rodent_control_status = ""

    # 石綿関連の初期値
    asbestos_level = ""
    asbestos_locations = ""
    asbestos_types = ""
    asbestos_survey_date = ""
    asbestos_survey_company = ""
    asbestos_surveyor = ""
    asbestos_area = ""
    # 下請負人の初期値
    subcontractor_name = ""
    subcontractor_address = ""
    subcontractor_tel = ""

    if is_demolition:
        st.markdown("**解体工事の詳細**")
        col_demo1, col_demo2 = st.columns(2)
        with col_demo1:
            construction_year = st.text_input("竣工年又は築年数",
                value=st.session_state.get("_asb_construction_year", ""),
                placeholder="昭和55年（築45年）",
                help="報告書の「解体建築物等の概要」に記載")
            renovation_history = st.text_input("増改築・改修歴", value="無", placeholder="平成10年 外壁改修",
                                               help="報告書に記載")
            demolition_method = st.selectbox("解体方法", [
                "圧砕機による機械解体",
                "手壊し解体（手作業）",
                "カッター工法",
                "転倒工法",
                "その他",
            ], help="標識（お知らせ看板）に記載")
        with col_demo2:
            asbestos_status = st.selectbox("石綿等の使用", [
                "無し",
                "有り",
                "調査中",
            ], help="標識・報告書に記載（☑/□で出力）")
            asbestos_removal_method = ""
            if asbestos_status == "有り":
                asbestos_removal_method = st.text_input("石綿等の除去方法",
                    value=st.session_state.get("_asb_removal_method", ""),
                    placeholder="隔離養生の上、湿潤化して手作業で除去",
                    help="石綿ありの場合に標識・報告書に記載")
            transport_route = st.text_input("搬出経路", placeholder="現場北側より○○通りへ搬出",
                                            help="標識に記載")
            vehicle_route = st.text_input("工事車両通行経路", placeholder="○○通り→△△交差点→□□通り",
                                          help="標識に記載")

        # --- 石綿詳細フィールド（上部のOCRで読み取り or 手動入力） ---
        st.markdown("---")
        st.markdown("**石綿（アスベスト）事前調査結果**")
        st.caption("上部の「書類をアップロードして自動入力」から石綿調査報告書を読み込めます。手動入力も可能です。")

        # 石綿詳細フィールド（OCR結果 or 手動入力）
        col_asb1, col_asb2 = st.columns(2)
        with col_asb1:
            asbestos_level = st.selectbox("石綿レベル", [
                "",
                "レベル1（吹付け材）",
                "レベル2（保温材・断熱材等）",
                "レベル3（成形板等）",
            ], index=0, help="レベル1が最も飛散リスクが高い",
               key="asbestos_level_select")
            # OCR結果があればselectboxの初期値に反映
            _ocr_level = st.session_state.get("_asb_level", "")
            if _ocr_level and not asbestos_level:
                st.caption(f"OCR読取値: {_ocr_level}")
            asbestos_locations = st.text_input("石綿含有箇所",
                value=st.session_state.get("_asb_locations", ""),
                placeholder="外壁サイディング、屋根スレート",
                help="カンマ区切りで複数箇所を入力")
            asbestos_types = st.text_input("石綿の種類",
                value=st.session_state.get("_asb_types", ""),
                placeholder="クリソタイル",
                help="検出された石綿の種類")
        with col_asb2:
            asbestos_survey_date = st.text_input("調査実施日",
                value=st.session_state.get("_asb_survey_date", ""),
                placeholder="令和8年2月15日")
            asbestos_survey_company = st.text_input("調査機関名",
                value=st.session_state.get("_asb_survey_company", ""),
                placeholder="○○環境分析センター")
            asbestos_surveyor = st.text_input("調査者名",
                value=st.session_state.get("_asb_surveyor", ""),
                placeholder="○○ ○○")
            asbestos_area = st.text_input("石綿使用面積（㎡）",
                value=st.session_state.get("_asb_area", ""),
                placeholder="120.5")

        # --- 区ごとの動的チェックボックス ---
        _ward_for_cb = detected_ward if detected_ward else ""
        _cb_defs = get_demolition_checkboxes(_ward_for_cb)
        # asbestos は上のselectboxで既に処理済みなのでスキップ
        _cb_defs_filtered = [d for d in _cb_defs if d["id"] != "asbestos"]

        if _cb_defs_filtered:
            st.markdown("**チェック項目（Wordに ☑/□ で出力）**")
            for cb_def in _cb_defs_filtered:
                cb_id = cb_def["id"]
                cb_label = cb_def["label"]
                cb_options = cb_def["options"]
                cb_type = cb_def["type"]

                if cb_type == "multi":
                    # 複数選択チェックボックス
                    st.caption(cb_label)
                    _selected = []
                    _cols = st.columns(len(cb_options))
                    for idx, opt in enumerate(cb_options):
                        with _cols[idx]:
                            if st.checkbox(opt, key=f"cb_{cb_id}_{idx}"):
                                _selected.append(opt)
                    # 変数に格納
                    if cb_id == "large_building":
                        large_building_checks = _selected
                    elif cb_id == "explanation_method":
                        explanation_method_checks = _selected
                    elif cb_id == "attachments":
                        attachment_checks = _selected
                    elif cb_id == "meeting_required":
                        pass  # 表示のみ（報告書のform_noteに反映済み）

                elif cb_type == "radio":
                    # 排他選択
                    _val = st.radio(cb_label, cb_options, horizontal=True,
                                    key=f"cb_{cb_id}")
                    if cb_id == "specific_construction":
                        specific_construction_status = _val
                    elif cb_id == "rodent_control":
                        rodent_control_status = _val

    else:
        construction_year = ""
        renovation_history = ""
        demolition_method = ""
        asbestos_status = ""
        asbestos_removal_method = ""
        transport_route = ""
        vehicle_route = ""

    # 戸数（区の様式で必要な場合のみ表示）
    if _show("unit_count") or _show("oneroom_count"):
        col_unit1, col_unit2 = st.columns(2)
        with col_unit1:
            if _show("unit_count"):
                unit_count = st.text_input("総住戸数", placeholder="30")
        with col_unit2:
            if _show("oneroom_count"):
                oneroom_count = st.text_input("ワンルーム戸数（40㎡未満）", placeholder="10")

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("工期")
        start_date = st.text_input("着工予定日", value=_ocr_val("start_date"), placeholder="令和8年5月1日", help=_field_help("start_date"))
        end_date = st.text_input("完了予定日", value=_ocr_val("end_date"), placeholder="令和8年10月31日", help=_field_help("end_date"))

        st.subheader("届出者（発注者・建築主）")
        applicant_name = st.text_input("届出者 氏名", value=_ocr_val("applicant_name"), placeholder="株式会社 ○○建設　代表取締役　○○ ○○", help=_field_help("applicant_name"))
        applicant_address = st.text_input("届出者 住所", value=_ocr_val("applicant_address"), placeholder="東京都千代田区○○1-1-1", help=_field_help("applicant_address"))
        applicant_tel = st.text_input("届出者 電話", value=_ocr_val("applicant_tel"), placeholder="03-0000-0001", help=_field_help("applicant_tel"))

    with col2:
        st.subheader("設計者")
        if is_demolition:
            st.caption("解体工事では設計者情報は不要です")
        designer_name = st.text_input("設計者名", value=_ocr_val("designer_name"), placeholder="○○設計事務所", help=_field_help("designer_name"), disabled=is_demolition)
        designer_tel = st.text_input("設計者 電話", value=_ocr_val("designer_tel"), placeholder="03-0000-0002", help=_field_help("designer_tel"), disabled=is_demolition)
        if is_demolition:
            designer_name = ""
            designer_tel = ""

        st.subheader("施工者")
        constructor_name = st.text_input("施工者名", value=_ocr_val("constructor_name"), placeholder="○○建設 株式会社", help=_field_help("constructor_name"))
        constructor_address = st.text_input("施工者 住所", placeholder="東京都○○区○○1-1-1",
                                             help="解体届出様式で必要な場合があります")
        constructor_tel = st.text_input("施工者 電話", value=_ocr_val("constructor_tel"), placeholder="03-1234-5678", help=_field_help("constructor_tel"))
        site_manager = st.text_input("現場責任者", value=_ocr_val("site_manager"), placeholder="○○ ○○", help=_field_help("site_manager"))

        # 下請負人（解体工事で必要な場合）
        if is_demolition:
            with st.expander("下請負人情報（該当する場合）", expanded=False):
                subcontractor_name = st.text_input("下請負人名", placeholder="○○解体工業")
                subcontractor_address = st.text_input("下請負人 住所", placeholder="東京都○○区○○2-2-2")
                subcontractor_tel = st.text_input("下請負人 電話", placeholder="03-9999-0000")

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        explanation_date = st.text_input("説明実施日", placeholder="令和8年3月15日", help=_field_help("explanation_date"))
        explanation_method = st.selectbox("説明方法", [
            "個別訪問による説明及び書面配布",
            "説明会の開催",
            "書面の配布（ポスティング）",
            "個別訪問による説明",
        ], help=_field_help("explanation_method"))
    with col2:
        target_count = st.text_input("説明対象戸数", placeholder="25", help=_field_help("target_count"))
        explained_count = st.text_input("説明済み戸数", placeholder="20", help=_field_help("explained_count"))
        unexplained_count = st.text_input("未説明戸数（不在等）", placeholder="5", help=_field_help("unexplained_count"))
    opinions = st.text_area("住民からの意見・要望", placeholder="特になし", height=100)

    # 届出期限の目安（説明はこの期限より前に完了させる必要がある）
    _dl_info = _calc_deadline_info(start_date, detected_ward)
    if _dl_info:
        st.info(
            f"**説明のスケジュール目安（{_dl_info['ward']}区）**\n\n"
            f"着工日 {_dl_info['start_date']} から逆算した届出期限:\n\n"
            + "\n\n".join(_dl_info["lines"])
            + f"\n\n近隣説明はこれらの期限 **より前** に完了させてください。\n\n※ {_dl_info['note']}"
        )

with tab4:
    col1, col2 = st.columns(2)
    with col1:
        submit_date = st.text_input("届出日", placeholder="令和8年3月10日", help=_field_help("submit_date"))
        sign_install_date = st.text_input("標識設置日", placeholder="令和8年3月10日", help=_field_help("sign_install_date"))
        work_hours = st.text_input("作業時間", value="午前8時00分 ～ 午後5時00分")
    with col2:
        holidays = st.text_input("休工日", value="日曜日・祝日")
        client_name = st.text_input("発注者名（工事のお知らせ用）", placeholder="株式会社 ○○建設")

    # 届出期限の目安
    _dl_info2 = _calc_deadline_info(start_date, detected_ward)
    if _dl_info2:
        st.warning(
            f"**届出期限の目安（{_dl_info2['ward']}区）**\n\n"
            f"着工日 {_dl_info2['start_date']} から逆算:\n\n"
            + "\n\n".join(_dl_info2["lines"])
            + f"\n\n届出日・標識設置日はこの期限に間に合うように設定してください。\n\n※ {_dl_info2['note']}"
        )

# ========== 入力チェックリスト ==========
st.divider()

# チェック対象フィールドと現在の入力値
_all_inputs = {
    "site_name": ("工事名称", site_name),
    "site_address": ("工事場所", site_address),
    "building_name": ("建物名称", building_name),
    "building_use": ("主要用途", building_use),
    "structure": ("構造", structure),
    "height": ("高さ", height),
    "floors_above": ("地上階数", floors_above),
    "floors_below": ("地下階数", floors_below),
    "site_area": ("敷地面積", site_area),
    "building_area": ("建築面積", building_area),
    "total_floor_area": ("延べ面積", total_floor_area),
    "construction_type": ("工事種別", construction_type),
    "foundation": ("基礎工法", foundation),
    "land_number": ("地名地番", land_number),
    "zoning": ("用途地域", zoning),
    "fire_zone": ("防火地域", fire_zone),
    "other_zone": ("その他の地域・地区", other_zone),
    "unit_count": ("総住戸数", unit_count),
    "oneroom_count": ("ワンルーム戸数", oneroom_count),
    "start_date": ("着工予定日", start_date),
    "end_date": ("完了予定日", end_date),
    "submit_date": ("届出日", submit_date),
    "sign_install_date": ("標識設置日", sign_install_date),
    "applicant_name": ("届出者 氏名", applicant_name),
    "applicant_address": ("届出者 住所", applicant_address),
    "applicant_tel": ("届出者 電話", applicant_tel),
    "designer_name": ("設計者名", designer_name),
    "designer_tel": ("設計者 電話", designer_tel),
    "constructor_name": ("施工者名", constructor_name),
    "constructor_tel": ("施工者 電話", constructor_tel),
    "site_manager": ("現場責任者", site_manager),
    "explanation_date": ("説明実施日", explanation_date),
    "explanation_method": ("説明方法", explanation_method),
    "target_count": ("説明対象戸数", target_count),
    "explained_count": ("説明済み戸数", explained_count),
    "unexplained_count": ("未説明戸数", unexplained_count),
    "opinions": ("住民からの意見・要望", opinions),
}

_active_req = _req_fields.copy() if _req_fields else set()
if is_demolition:
    # 解体時: 標識設置届のみで必要なフィールドを除外
    _sign_only = _rf_sign - _rf_report if "_rf_sign" in dir() and "_rf_report" in dir() else set()
    _active_req -= _sign_only
    _active_req.discard("designer_name")
    _active_req.discard("designer_tel")

if _active_req:
    # 必須フィールドのうち入力済み・未入力を集計
    _filled = []
    _missing = []
    for fid in sorted(_active_req):
        if fid in _all_inputs:
            label, val = _all_inputs[fid]
            if val and val.strip():
                _filled.append(label)
            else:
                _missing.append(label)

    _total = len(_filled) + len(_missing)
    _ward_suffix = detected_ward_full if "detected_ward_full" in dir() else detected_ward

    with st.expander(
        f"入力チェックリスト（{_ward_suffix}様式）— {len(_filled)}/{_total} 項目入力済み",
        expanded=bool(_missing),
    ):
        if _missing:
            st.warning(f"未入力: {len(_missing)} 項目")
            _missing_str = "　".join([f"- [ ] {m}" for m in _missing])
            # 2列でチェックリスト表示
            _mid = (len(_missing) + 1) // 2
            _ck_col1, _ck_col2 = st.columns(2)
            with _ck_col1:
                for m in _missing[:_mid]:
                    st.markdown(f"- [ ] {m}")
            with _ck_col2:
                for m in _missing[_mid:]:
                    st.markdown(f"- [ ] {m}")
        if _filled:
            st.success(f"入力済み: {len(_filled)} 項目")
            _mid2 = (len(_filled) + 1) // 2
            _ck_col3, _ck_col4 = st.columns(2)
            with _ck_col3:
                for f in _filled[:_mid2]:
                    st.markdown(f"- [x] {f}")
            with _ck_col4:
                for f in _filled[_mid2:]:
                    st.markdown(f"- [x] {f}")
        st.caption("※ 未入力でも書類は生成できますが、該当欄が空欄になります。")

st.markdown('<div class="step-header"><div class="step-number">4</div><div class="step-title">書類生成</div></div>', unsafe_allow_html=True)
if st.button("書類を一括生成", type="primary", use_container_width=True):
    if not site_name or not site_address:
        st.error("「工事名称」と「工事場所」は必須です。")
        st.stop()

    if not detected_coords:
        st.error("住所から位置情報を取得できませんでした。住所を確認してください。")
        st.stop()

    # マーカー位置（ユーザーが修正した場合はそちらを使用）
    lat = st.session_state.get("marker_lat", detected_coords[0])
    lng = st.session_state.get("marker_lng", detected_coords[1])
    ward = ward_name_input or detected_ward

    data = {
        "site_name": site_name,
        "site_address": site_address,
        "lat": lat,
        "lng": lng,
        "radius_m": radius_m,
        "is_demolition": is_demolition,
        "work_content": work_content or ("建物の解体工事" if is_demolition else "建物の新築工事"),
        "building_name": building_name or site_name.replace("工事", ""),
        "building_use": building_use or "",
        "structure": structure,
        "foundation": foundation,
        "construction_type": construction_type,
        "floors_above": floors_above or "",
        "floors_below": floors_below or "",
        "height": height or "",
        "site_area": site_area or "",
        "building_area": building_area or "",
        "total_floor_area": total_floor_area or "",
        "land_number": land_number or "",
        "zoning": zoning or "",
        "fire_zone": fire_zone or "",
        "other_zone": other_zone or "",
        "unit_count": unit_count or "",
        "oneroom_count": oneroom_count or "",
        "start_date": start_date or "",
        "end_date": end_date or "",
        "work_hours": work_hours,
        "holidays": holidays,
        "ward_name": ward,
        "submit_date": submit_date or "",
        "sign_install_date": sign_install_date or "",
        "sign_location": "建築予定地の道路に面する見やすい場所",
        "applicant_name": applicant_name or "",
        "applicant_address": applicant_address or "",
        "applicant_tel": applicant_tel or "",
        "client_name": client_name or "",
        "designer_name": designer_name or "",
        "designer_tel": designer_tel or "",
        "constructor_name": constructor_name or "",
        "constructor_tel": constructor_tel or "",
        "site_manager": site_manager or "",
        "explanation_date": explanation_date or "",
        "explanation_method": explanation_method,
        "target_count": target_count or "",
        "explained_count": explained_count or "",
        "unexplained_count": unexplained_count or "",
        "opinions": opinions or "特になし",
        # 解体専用フィールド
        "construction_year": construction_year or "",
        "renovation_history": renovation_history or "無",
        "demolition_method": demolition_method or "",
        "asbestos_status": asbestos_status or "",
        "asbestos_removal_method": asbestos_removal_method or "",
        "transport_route": transport_route or "",
        "vehicle_route": vehicle_route or "",
        "constructor_address": constructor_address or "",
        "subcontractor_name": subcontractor_name if is_demolition else "",
        "subcontractor_address": subcontractor_address if is_demolition else "",
        "subcontractor_tel": subcontractor_tel if is_demolition else "",
        # 石綿詳細
        "asbestos_level": asbestos_level or "",
        "asbestos_locations": asbestos_locations or "",
        "asbestos_types": asbestos_types or "",
        "asbestos_survey_date": asbestos_survey_date or "",
        "asbestos_survey_company": asbestos_survey_company or "",
        "asbestos_surveyor": asbestos_surveyor or "",
        "asbestos_area": asbestos_area or "",
        # 解体用チェックボックス値
        "large_building_checks": large_building_checks,
        "explanation_method_checks": explanation_method_checks,
        "attachment_checks": attachment_checks,
        "specific_construction_status": specific_construction_status,
        "rodent_control_status": rodent_control_status,
    }

    with st.spinner("書類を生成中..."):
        try:
            tmpdir = tempfile.mkdtemp()
            progress = st.progress(0, text="近隣説明範囲図を生成中...")

            # 1. 地図（プレビューと同じズーム・地図種類を反映）
            selected_tile = tile_choice if "tile_choice" in dir() else "国土地理院（標準）"
            # プレビューで操作中のズームがあればそれを使う
            final_zoom = st.session_state.get("_map_zoom") or _calc_zoom(radius_m, zoom_offset=zoom_adjust if "zoom_adjust" in dir() else 0)
            map_png = generate_map_png(
                site_name=data["site_name"],
                address=data["site_address"],
                lat=lat,
                lng=lng,
                radius_m=radius_m,
                output_dir=tmpdir,
                zoom_override=final_zoom,
                tile_name=selected_tile,
                building_pins=st.session_state.get("building_pins", []),
                sign_pins=st.session_state.get("sign_pins", []),
            )
            if is_demolition:
                map_docx = os.path.join(tmpdir, "01_解体工事現場案内図.docx")
                generate_map_document(data, map_png, map_docx,
                                      building_pins=st.session_state.get("building_pins", []),
                                      title="解体工事現場案内図（標識設置位置図）")
            else:
                map_docx = os.path.join(tmpdir, "01_近隣説明範囲図.docx")
                generate_map_document(data, map_png, map_docx,
                                      building_pins=st.session_state.get("building_pins", []))
            progress.progress(25, text="標識設置届を生成中...")

            # 2. 標識設置届 or 解体書類
            from template_filler import get_available_templates
            tpl = get_available_templates(ward)
            sign_path = None
            demolition_report_path = None
            demolition_sign_path = None
            if is_demolition:
                # 解体: お知らせ標識 + 事前周知報告書を生成
                # テンプレートがxlsx/docxどちらかで出力される可能性がある
                demolition_sign_path = os.path.join(tmpdir, "02_解体工事のお知らせ標識.docx")
                result_sign = generate_demolition_sign(data, demolition_sign_path)
                if result_sign and result_sign != demolition_sign_path:
                    demolition_sign_path = result_sign  # xlsx等で出力された場合
                demolition_report_path = os.path.join(tmpdir, "03_解体工事事前周知報告書.docx")
                result_report = generate_demolition_report(data, demolition_report_path)
                if result_report and result_report != demolition_report_path:
                    demolition_report_path = result_report
            else:
                sign_ext = ".xlsx" if tpl["sign_notice"] == "xlsx" else ".docx"
                sign_path = os.path.join(tmpdir, f"02_標識設置届{sign_ext}")
                generate_sign_notice(data, sign_path)
            progress.progress(50, text="近隣説明報告書を生成中..." if not is_demolition else "工事のお知らせを生成中...")

            # 3. 報告書（新築のみ。解体は事前周知報告書で代替済み）
            report_path = None
            if not is_demolition:
                report_ext = ".xlsx" if tpl["report"] == "xlsx" else ".docx"
                report_path = os.path.join(tmpdir, f"03_近隣説明報告書{report_ext}")
                generate_explanation_report(data, report_path)
            progress.progress(75, text="工事のお知らせを生成中...")

            # 4. お知らせ
            notice_docx = os.path.join(tmpdir, "04_工事のお知らせ.docx")
            generate_construction_notice(data, notice_docx)
            progress.progress(80, text="近隣施設を検索中...")

            # 5. 近隣施設リスト
            nearby_data = search_nearby(lat, lng, radius_m)
            nearby_text = format_nearby_list(nearby_data)
            nearby_path = os.path.join(tmpdir, "05_近隣施設一覧.txt")
            with open(nearby_path, "w", encoding="utf-8") as f:
                f.write(f"近隣説明範囲内の施設・建物一覧\n")
                f.write(f"工事名: {site_name}\n")
                f.write(f"工事場所: {site_address}\n")
                f.write(f"説明範囲: 半径{radius_m}m\n")
                f.write(f"{'=' * 50}\n\n")
                f.write(nearby_text)
            progress.progress(100, text="完了！")

            # ZIPにまとめる
            if is_demolition:
                # 実際に生成されたファイル名を使用（xlsx/docx対応）
                _sign_fname = os.path.basename(demolition_sign_path) if demolition_sign_path else "02_解体工事のお知らせ標識.docx"
                _report_fname = os.path.basename(demolition_report_path) if demolition_report_path else "03_解体工事事前周知報告書.docx"
                _zip_files = [
                    "01_解体工事現場案内図.docx",
                    _sign_fname,
                    _report_fname,
                    "04_工事のお知らせ.docx",
                    "05_近隣施設一覧.txt",
                    "近隣説明範囲図.png",
                ]
            else:
                _zip_files = [
                    "01_近隣説明範囲図.docx",
                    "04_工事のお知らせ.docx",
                    "05_近隣施設一覧.txt",
                    "近隣説明範囲図.png",
                ]
                sign_ext = ".xlsx" if tpl["sign_notice"] == "xlsx" else ".docx"
                _zip_files.insert(1, f"02_標識設置届{sign_ext}")
                report_ext = ".xlsx" if tpl["report"] == "xlsx" else ".docx"
                _zip_files.insert(2, f"03_近隣説明報告書{report_ext}")
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for fname in _zip_files:
                    fpath = os.path.join(tmpdir, fname)
                    if os.path.exists(fpath):
                        zf.write(fpath, fname)
            zip_buffer.seek(0)

            if is_demolition:
                st.success("解体工事用の書類を生成しました！（お知らせ標識 + 事前周知報告書 + 範囲図 + チラシ）")
                _demo_url = _wc_for_url.get("demolition_url", "") if "_wc_for_url" in dir() else ""
                if _demo_url:
                    st.info(
                        f"**お知らせ標識はA3以上に拡大して印刷してください。**\n\n"
                        f"公式サイトで最新の様式・記載要件を確認することをおすすめします。"
                        f"\n\n🔗 [{_demo_url}]({_demo_url})"
                    )
                else:
                    st.info(
                        f"**この自治体には独自の解体事前周知制度がありません。**\n\n"
                        f"建設リサイクル法に基づく届出（東京都多摩建築指導事務所）が必要です。\n\n"
                        f"生成した書類は汎用様式です。提出前に管轄窓口にご確認ください。"
                    )
            else:
                st.success("書類の生成が完了しました！")

            safe_name = site_name.replace("/", "_").replace("\\", "_")
            st.download_button(
                label="📥 書類一式をダウンロード（ZIP）",
                data=zip_buffer,
                file_name=f"近隣説明会_{safe_name}.zip",
                mime="application/zip",
                type="primary",
                use_container_width=True,
            )

            with st.expander("📋 生成した書類の一覧", expanded=True):
                if is_demolition:
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("近隣説明範囲図", "01_.docx")
                    col2.metric("お知らせ標識", "02_.docx")
                    col3.metric("事前周知報告書", "03_.docx")
                    col4.metric("工事のお知らせ", "04_.docx")
                else:
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("近隣説明範囲図", "01_.docx")
                    col2.metric("標識設置届", "02_.docx")
                    col3.metric("近隣説明報告書", "03_.docx")
                    col4.metric("工事のお知らせ", "04_.docx")

            if os.path.exists(map_png):
                with st.expander("🗺️ 近隣説明範囲図プレビュー", expanded=True):
                    st.image(map_png, caption=f"近隣説明範囲図 - {site_name}（半径{radius_m}m）")

            # 近隣施設リスト表示
            if nearby_data:
                with st.expander("🏘️ 近隣施設・建物一覧（範囲内）", expanded=True):
                    priority = [
                        "医療施設", "教育施設", "福祉施設", "宗教施設",
                        "集合住宅", "戸建て住宅",
                        "店舗・商業施設", "事務所・商業ビル",
                        "公園・レジャー",
                    ]
                    shown = set()
                    for cat in priority:
                        if cat in nearby_data:
                            items = nearby_data[cat]
                            named = [i for i in items if i["name"]]
                            unnamed_count = len(items) - len(named)
                            st.markdown(f"**{cat}**")
                            for item in named:
                                addr_part = f"（{item['address']}）" if item["address"] else ""
                                st.markdown(f"- {item['name']}{addr_part}")
                            if unnamed_count > 0:
                                st.markdown(f"- 他 {unnamed_count}件（名称不明）")
                            shown.add(cat)
                    for cat in sorted(nearby_data.keys()):
                        if cat not in shown:
                            items = nearby_data[cat]
                            named = [i for i in items if i["name"]]
                            unnamed_count = len(items) - len(named)
                            st.markdown(f"**{cat}**")
                            for item in named:
                                addr_part = f"（{item['address']}）" if item["address"] else ""
                                st.markdown(f"- {item['name']}{addr_part}")
                            if unnamed_count > 0:
                                st.markdown(f"- 他 {unnamed_count}件（名称不明）")
                    st.caption("※ OpenStreetMapのデータに基づく参考情報です。現地確認で正確な対象範囲を特定してください。")

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
            raise

# ========== フッター ==========
st.markdown("---")
st.markdown("""
<div class="footer-disclaimer">
    <strong>免責事項</strong><br>
    本システムは届出書類の作成を補助するツールです。生成された書類が最新の規定に適合しているとは限りません。
    届出前に必ず管轄の行政窓口で様式・記載内容をご確認ください。
    本システムの利用により生じた損害について、開発者は一切の責任を負いません。
    <div style="margin-top:0.8rem; font-size:0.7rem; color:#94a3b8;">KINRIN v1.0 &mdash; 東京23区 + 多摩26市 対応</div>
</div>
""", unsafe_allow_html=True)
