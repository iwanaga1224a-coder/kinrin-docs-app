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
import streamlit as st
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
st.caption("住所と工事情報を入力するだけで、届出書類4点セットをWord形式で一括生成します")

# ========== サイドバー ==========
st.sidebar.header("📋 このアプリの流れ")
st.sidebar.markdown("""
**① 住所を入力**
→ 区を自動判定、緯度経度を自動取得

**② 届出ルールを確認**
→ 区ごとに説明範囲・届出先が異なります
→ 各区の窓口で最新ルールをご確認ください

**③ 書類を生成**
→ Word 4点セット + 地図PNG をZIPでダウンロード
""")
st.sidebar.divider()
st.sidebar.markdown("""
**生成する書類:**
1. 近隣説明範囲図（地図付き）
2. 標識設置届
3. 近隣説明報告書
4. 工事のお知らせ
""")
st.sidebar.divider()
st.sidebar.warning("生成した書類は叩き台です。届出前に必ず管轄窓口でご確認ください。")

# ========== STEP 1：住所入力 ==========
st.header("① 工事場所と基本情報")

col_addr1, col_addr2 = st.columns([3, 1])
with col_addr1:
    site_address = st.text_input("工事場所（住所） *", placeholder="東京都新宿区西新宿2-8-1")
with col_addr2:
    site_name = st.text_input("工事名称 *", placeholder="○○ビル解体工事")

# 住所から自動判定
detected_ward = ""
detected_coords = None
if site_address:
    detected_ward = extract_ward(site_address)
    detected_ward_full = extract_ward_with_suffix(site_address)
    detected_coords = geocode(site_address)

    if detected_ward:
        st.success(f"届出先: **{detected_ward_full}** （自動判定）")
    else:
        st.warning("区名を判定できませんでした。手動で入力してください。")
    if not detected_coords:
        st.warning("住所から位置を取得できませんでした。住所を確認してください。")

# ========== STEP 2：届出ルール ==========
st.header("② 届出ルールの確認")

st.info(
    "近隣説明の範囲・届出先の部署は**区ごとに異なります**。\n\n"
    "- 半径○mの円で指定する区\n"
    "- 建物高さを敷地境界から倒した範囲で指定する区\n"
    "- 高さ10m超で中高層条例が適用される区\n\n"
    "各区の建築課・環境対策課等の窓口で最新のルール・ひな形をご確認ください。\n"
    "ここでは範囲を手動で設定できます。"
)

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

# ========== 地図プレビュー ==========
if detected_coords:
    st.subheader("地図プレビュー")
    st.caption("拡大・縮小・移動で調整してください。この表示範囲が書類の地図に反映されます。")

    col_map_opt1, col_map_opt2 = st.columns([2, 1])
    with col_map_opt1:
        tile_choice = st.radio("地図の種類", list(TILE_PROVIDERS.keys()), horizontal=True, index=0)
    with col_map_opt2:
        map_scale = st.slider("拡大倍率", min_value=1.0, max_value=4.0, value=1.0, step=0.5,
                              help="1.0が標準。大きくすると地図をさらに拡大して出力します")

    preview_lat, preview_lng = detected_coords
    preview_zoom = _calc_zoom(radius_m)

    tile_info = TILE_PROVIDERS[tile_choice]
    if tile_info["attr"]:
        preview_map = folium.Map(
            location=[preview_lat, preview_lng],
            zoom_start=preview_zoom,
            tiles=tile_info["tiles"],
            attr=tile_info["attr"],
        )
    else:
        preview_map = folium.Map(
            location=[preview_lat, preview_lng],
            zoom_start=preview_zoom,
            tiles=tile_info["tiles"],
        )

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
        popup=f"{site_name or '工事現場'}<br>{site_address}",
        icon=DivIcon(
            html='<div style="font-size:28px;color:red;text-shadow:1px 1px 2px rgba(0,0,0,0.5);transform:translate(-14px,-14px);">&#9733;</div>',
            icon_size=(30, 30),
            icon_anchor=(0, 0),
        ),
    ).add_to(preview_map)

    # インタラクティブ地図を表示、ユーザーの操作後のzoomとcenterを取得
    map_output = st_folium(preview_map, width=800, height=500, returned_objects=[])

    # ユーザーが操作した後のzoom/centerをsession_stateに保存
    if map_output and map_output.get("zoom"):
        st.session_state["confirmed_zoom"] = map_output["zoom"]
    if map_output and map_output.get("center"):
        st.session_state["confirmed_center"] = map_output["center"]

# ========== STEP 3：工事情報入力 ==========
st.header("③ 工事情報の入力")

tab1, tab2, tab3, tab4 = st.tabs([
    "建物・工事内容",
    "工期・関係者",
    "説明実施情報",
    "オプション",
])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        work_content = st.text_input("工事内容", placeholder="鉄筋コンクリート造建物の解体工事")
        building_name = st.text_input("建物名称", placeholder="○○ビル")
        building_use = st.text_input("用途", placeholder="事務所")
    with col2:
        structure = st.selectbox("構造", ["鉄筋コンクリート造", "鉄骨造", "鉄骨鉄筋コンクリート造", "木造", "その他"])
        floors_above = st.text_input("地上階数", placeholder="6")
        floors_below = st.text_input("地下階数", placeholder="1")

    col3, col4, col5, col6 = st.columns(4)
    with col3:
        height = st.text_input("高さ（m）", placeholder="22.5")
    with col4:
        site_area = st.text_input("敷地面積（㎡）", placeholder="500.00")
    with col5:
        building_area = st.text_input("建築面積（㎡）", placeholder="350.00")
    with col6:
        total_floor_area = st.text_input("延べ面積（㎡）", placeholder="2,100.00")

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("工期")
        start_date = st.text_input("着工予定日", placeholder="令和8年5月1日")
        end_date = st.text_input("完了予定日", placeholder="令和8年10月31日")

        st.subheader("届出者（発注者・建築主）")
        applicant_name = st.text_input("届出者 氏名", placeholder="株式会社 ○○建設　代表取締役　○○ ○○")
        applicant_address = st.text_input("届出者 住所", placeholder="東京都千代田区○○1-1-1")
        applicant_tel = st.text_input("届出者 電話", placeholder="03-0000-0001")

    with col2:
        st.subheader("設計者")
        designer_name = st.text_input("設計者名", placeholder="○○設計事務所")
        designer_tel = st.text_input("設計者 電話", placeholder="03-0000-0002")

        st.subheader("施工者")
        constructor_name = st.text_input("施工者名", placeholder="○○建設 株式会社")
        constructor_tel = st.text_input("施工者 電話", placeholder="03-1234-5678")
        site_manager = st.text_input("現場責任者", placeholder="○○ ○○")

with tab3:
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

with tab4:
    col1, col2 = st.columns(2)
    with col1:
        work_hours = st.text_input("作業時間", value="午前8時00分 ～ 午後5時00分")
        holidays = st.text_input("休工日", value="日曜日・祝日")
    with col2:
        submit_date = st.text_input("届出日", placeholder="令和8年3月10日")
        sign_install_date = st.text_input("標識設置日", placeholder="令和8年3月10日")
        client_name = st.text_input("発注者名（工事のお知らせ用）", placeholder="株式会社 ○○建設")

# ========== 生成ボタン ==========
st.divider()

if st.button("📄 書類を生成する", type="primary", use_container_width=True):
    if not site_name or not site_address:
        st.error("「工事名称」と「工事場所」は必須です。")
        st.stop()

    if not detected_coords:
        st.error("住所から位置情報を取得できませんでした。住所を確認してください。")
        st.stop()

    lat, lng = detected_coords
    ward = ward_name_input or detected_ward

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
    }

    with st.spinner("書類を生成中..."):
        try:
            tmpdir = tempfile.mkdtemp()
            progress = st.progress(0, text="近隣説明範囲図を生成中...")

            # 1. 地図（プレビューと同じ地図種類・拡大倍率を反映）
            selected_tile = tile_choice if "tile_choice" in dir() else "国土地理院（標準）"
            user_scale = map_scale if "map_scale" in dir() else 1.0
            map_png = generate_map_png(
                site_name=data["site_name"],
                address=data["site_address"],
                lat=lat,
                lng=lng,
                radius_m=radius_m,
                output_dir=tmpdir,
                tile_name=selected_tile,
                scale=user_scale,
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
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for fname in [
                    "01_近隣説明範囲図.docx",
                    "02_標識設置届.docx",
                    "03_近隣説明報告書.docx",
                    "04_工事のお知らせ.docx",
                    "05_近隣施設一覧.txt",
                    "近隣説明範囲図.png",
                ]:
                    fpath = os.path.join(tmpdir, fname)
                    if os.path.exists(fpath):
                        zf.write(fpath, fname)
            zip_buffer.seek(0)

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
st.divider()
st.caption("※ このアプリで生成した書類は叩き台です。届出前に必ず管轄の行政窓口で様式・記載内容をご確認ください。")
