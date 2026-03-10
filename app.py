# -*- coding: utf-8 -*-
"""近隣説明会 書類生成アプリ（Streamlit）"""

import os
import io
import sys
import zipfile
import tempfile
import streamlit as st

# 同じディレクトリのモジュール
sys.path.insert(0, os.path.dirname(__file__))
from map_generator import generate_map_png
from doc_generator import (
    generate_sign_notice,
    generate_explanation_report,
    generate_construction_notice,
    generate_map_document,
)

# ========== ページ設定 ==========
st.set_page_config(
    page_title="近隣説明会 書類生成",
    page_icon="🏗️",
    layout="wide",
)

st.title("🏗️ 近隣説明会 書類生成アプリ")
st.caption("工事情報を入力するだけで、届出書類4点セットをWord形式で一括生成します")

# ========== サイドバー ==========
st.sidebar.header("📋 生成する書類")
st.sidebar.markdown("""
1. **近隣説明範囲図**（地図付き）
2. **標識設置届**
3. **近隣説明報告書**
4. **工事のお知らせ**
""")
st.sidebar.divider()
st.sidebar.info("入力後「書類を生成する」ボタンを押してください。\nZIPファイルでまとめてダウンロードできます。")

# ========== 入力フォーム ==========
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "① 工事基本情報",
    "② 建物情報",
    "③ 工期・関係者",
    "④ 説明実施情報",
    "⑤ オプション",
])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        site_name = st.text_input("工事名称 *", placeholder="○○ビル解体工事")
        site_address = st.text_input("工事場所（住所） *", placeholder="東京都新宿区西新宿2-8-1")
        ward_name = st.text_input("届出先の区名", placeholder="新宿")
    with col2:
        work_content = st.text_input("工事内容", placeholder="鉄筋コンクリート造建物の解体工事")
        lat = st.number_input("緯度", value=35.6896, format="%.4f", help="住所から検索: https://www.geocoding.jp/")
        lng = st.number_input("経度", value=139.6917, format="%.4f")

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        building_name = st.text_input("建物名称", placeholder="○○ビル")
        building_use = st.text_input("用途", placeholder="事務所")
        structure = st.selectbox("構造", ["鉄筋コンクリート造", "鉄骨造", "鉄骨鉄筋コンクリート造", "木造", "その他"])
    with col2:
        floors_above = st.text_input("地上階数", placeholder="6")
        floors_below = st.text_input("地下階数", placeholder="1")
        height = st.text_input("高さ（m）", placeholder="22.5")

    col3, col4, col5 = st.columns(3)
    with col3:
        site_area = st.text_input("敷地面積（㎡）", placeholder="500.00")
    with col4:
        building_area = st.text_input("建築面積（㎡）", placeholder="350.00")
    with col5:
        total_floor_area = st.text_input("延べ面積（㎡）", placeholder="2,100.00")

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("工期")
        start_date = st.text_input("着工予定日", placeholder="令和8年5月1日")
        end_date = st.text_input("完了予定日", placeholder="令和8年10月31日")

    with col2:
        st.subheader("届出者（発注者・建築主）")
        applicant_name = st.text_input("届出者 氏名", placeholder="株式会社 ○○建設　代表取締役　○○ ○○")
        applicant_address = st.text_input("届出者 住所", placeholder="東京都千代田区○○1-1-1")
        applicant_tel = st.text_input("届出者 電話", placeholder="03-0000-0001")

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("設計者")
        designer_name = st.text_input("設計者名", placeholder="○○設計事務所")
        designer_tel = st.text_input("設計者 電話", placeholder="03-0000-0002")

    with col4:
        st.subheader("施工者")
        constructor_name = st.text_input("施工者名", placeholder="○○建設 株式会社")
        constructor_tel = st.text_input("施工者 電話", placeholder="03-1234-5678")
        site_manager = st.text_input("現場責任者", placeholder="○○ ○○")

with tab4:
    col1, col2 = st.columns(2)
    with col1:
        explanation_date = st.text_input("説明実施日", placeholder="令和8年3月15日")
        explanation_method = st.selectbox("説明方法", [
            "個別訪問による説明及び書面配布",
            "説明会の開催",
            "書面の配布（ポスティング）",
            "個別訪問による説明",
        ])
    with col2:
        target_count = st.text_input("説明対象戸数", placeholder="25")
        explained_count = st.text_input("説明済み戸数", placeholder="20")
        unexplained_count = st.text_input("未説明戸数（不在等）", placeholder="5")

    opinions = st.text_area("住民からの意見・要望", placeholder="特になし", height=100)

with tab5:
    col1, col2 = st.columns(2)
    with col1:
        radius_m = st.slider("説明範囲（半径m）", min_value=10, max_value=200, value=50, step=10)
        work_hours = st.text_input("作業時間", value="午前8時00分 ～ 午後5時00分")
        holidays = st.text_input("休工日", value="日曜日・祝日")
    with col2:
        submit_date = st.text_input("届出日", placeholder="令和8年3月10日")
        sign_install_date = st.text_input("標識設置日", placeholder="令和8年3月10日")
        client_name = st.text_input("発注者名（工事のお知らせ用）", placeholder="株式会社 ○○建設")

# ========== 生成ボタン ==========
st.divider()

if st.button("📄 書類を生成する", type="primary", use_container_width=True):
    # バリデーション
    if not site_name or not site_address:
        st.error("「工事名称」と「工事場所」は必須です。")
        st.stop()

    # データ辞書を組み立て
    data = {
        "site_name": site_name,
        "site_address": site_address,
        "lat": lat,
        "lng": lng,
        "radius_m": radius_m,
        "work_content": work_content or "建物の解体工事",
        "building_name": building_name or site_name.replace("工事", ""),
        "building_use": building_use or "",
        "structure": structure,
        "floors_above": floors_above or "",
        "floors_below": floors_below or "",
        "height": height or "",
        "site_area": site_area or "",
        "building_area": building_area or "",
        "total_floor_area": total_floor_area or "",
        "start_date": start_date or "",
        "end_date": end_date or "",
        "work_hours": work_hours,
        "holidays": holidays,
        "ward_name": ward_name or "",
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
    }

    with st.spinner("書類を生成中..."):
        try:
            tmpdir = tempfile.mkdtemp()

            progress = st.progress(0, text="近隣説明範囲図を生成中...")

            # 1. 地図
            map_png = generate_map_png(
                site_name=data["site_name"],
                address=data["site_address"],
                lat=data["lat"],
                lng=data["lng"],
                radius_m=data["radius_m"],
                output_dir=tmpdir,
            )
            map_docx = os.path.join(tmpdir, "01_近隣説明範囲図.docx")
            generate_map_document(data, map_png, map_docx)
            progress.progress(25, text="標識設置届を生成中...")

            # 2. 標識設置届
            sign_docx = os.path.join(tmpdir, "02_標識設置届.docx")
            generate_sign_notice(data, sign_docx)
            progress.progress(50, text="近隣説明報告書を生成中...")

            # 3. 報告書
            report_docx = os.path.join(tmpdir, "03_近隣説明報告書.docx")
            generate_explanation_report(data, report_docx)
            progress.progress(75, text="工事のお知らせを生成中...")

            # 4. お知らせ
            notice_docx = os.path.join(tmpdir, "04_工事のお知らせ.docx")
            generate_construction_notice(data, notice_docx)
            progress.progress(100, text="完了！")

            # ZIPにまとめる
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for fname in [
                    "01_近隣説明範囲図.docx",
                    "02_標識設置届.docx",
                    "03_近隣説明報告書.docx",
                    "04_工事のお知らせ.docx",
                    "近隣説明範囲図.png",
                ]:
                    fpath = os.path.join(tmpdir, fname)
                    if os.path.exists(fpath):
                        zf.write(fpath, fname)
            zip_buffer.seek(0)

            st.success("書類の生成が完了しました！")

            # ダウンロードボタン
            safe_name = site_name.replace("/", "_").replace("\\", "_")
            st.download_button(
                label="📥 書類一式をダウンロード（ZIP）",
                data=zip_buffer,
                file_name=f"近隣説明会_{safe_name}.zip",
                mime="application/zip",
                type="primary",
                use_container_width=True,
            )

            # プレビュー
            with st.expander("📋 生成した書類の一覧", expanded=True):
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("近隣説明範囲図", "01_.docx")
                col2.metric("標識設置届", "02_.docx")
                col3.metric("近隣説明報告書", "03_.docx")
                col4.metric("工事のお知らせ", "04_.docx")

            # 地図プレビュー
            if os.path.exists(map_png):
                with st.expander("🗺️ 近隣説明範囲図プレビュー", expanded=True):
                    st.image(map_png, caption=f"近隣説明範囲図 - {site_name}（半径{radius_m}m）")

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
            raise

# ========== フッター ==========
st.divider()
st.caption("※ このアプリで生成した書類は叩き台です。届出前に必ず管轄の行政窓口で様式・記載内容をご確認ください。")
