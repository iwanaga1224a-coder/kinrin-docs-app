# -*- coding: utf-8 -*-
"""近隣説明範囲図 生成モジュール
Folium地図 → ヘッドレスChromeでPNG → Word埋め込み対応
"""

import os
import math
import time
import tempfile
import folium
from folium import Circle, Marker, DivIcon
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def _calc_zoom(radius_m):
    """半径(m)に応じた最適なズームレベルを計算
    円が画面の40〜60%くらいを占めるサイズにする
    """
    if radius_m <= 0:
        return 19
    # 画面の半分に円が収まるように計算
    # zoom 18 ≒ 約100m幅、zoom毎に2倍
    target_screen_m = radius_m * 3.5  # 円の直径+余白
    # OpenStreetMapの1ピクセルあたりのメートル: 156543.03 * cos(lat) / 2^zoom
    # 東京(lat≒35.7): cos(35.7°) ≒ 0.812
    # 画面幅1200px想定
    for z in range(20, 10, -1):
        meters_per_px = 156543.03 * 0.812 / (2 ** z)
        screen_m = meters_per_px * 1200
        if screen_m >= target_screen_m:
            return z
    return 14


def _label_offset(radius_m):
    """半径に応じたラベルのオフセット（緯度方向）"""
    # 1度 ≒ 111,000m
    return max(radius_m * 1.3, 15) / 111000


TILE_PROVIDERS = {
    "Google Maps": {
        "tiles": "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        "attr": "Google Maps",
    },
    "Google 航空写真": {
        "tiles": "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        "attr": "Google Maps",
    },
    "OpenStreetMap": {
        "tiles": "OpenStreetMap",
        "attr": None,
    },
}


def generate_map_html(site_name, address, lat, lng, radius_m=50, zoom_override=None, tile_name="Google Maps"):
    """Foliumで近隣説明範囲図HTMLを生成し、一時ファイルパスを返す"""
    zoom = zoom_override if zoom_override else _calc_zoom(radius_m)

    tile_info = TILE_PROVIDERS.get(tile_name, TILE_PROVIDERS["Google Maps"])

    if tile_info["attr"]:
        m = folium.Map(
            location=[lat, lng],
            zoom_start=zoom,
            tiles=tile_info["tiles"],
            attr=tile_info["attr"],
            width="100%",
            height="100%",
        )
    else:
        m = folium.Map(
            location=[lat, lng],
            zoom_start=zoom,
            tiles=tile_info["tiles"],
            width="100%",
            height="100%",
        )

    # タイトル（地図上部）
    title_html = f"""
    <div style="
        position: fixed;
        top: 10px; left: 50%;
        transform: translateX(-50%);
        z-index: 9999;
        background: white;
        border: 2px solid #333;
        padding: 8px 20px;
        font-size: 16px;
        font-weight: bold;
        font-family: 'Yu Gothic', 'MS Gothic', sans-serif;
        box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
    ">
        近隣説明範囲図　｜　{site_name}
    </div>
    """
    m.get_root().html.add_child(folium.Element(title_html))

    # 凡例（右下）
    legend_html = f"""
    <div style="
        position: fixed;
        bottom: 30px; right: 10px;
        z-index: 9999;
        background: white;
        border: 2px solid #333;
        padding: 10px 14px;
        font-size: 12px;
        font-family: 'Yu Gothic', 'MS Gothic', sans-serif;
        line-height: 1.8;
        box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
    ">
        <b>凡例</b><br>
        <span style="color:red;">&#9733;</span> 工事現場<br>
        <span style="color:red;">&#9675;</span> 近隣説明範囲（半径{radius_m}m）<br>
        <hr style="margin:4px 0;">
        工事名: {site_name}<br>
        所在地: {address}<br>
        範囲: 半径{radius_m}m
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    # 近隣説明範囲（赤い円）
    Circle(
        location=[lat, lng],
        radius=radius_m,
        color="red",
        weight=3,
        fill=True,
        fill_color="red",
        fill_opacity=0.08,
        popup=f"近隣説明範囲（半径{radius_m}m）",
    ).add_to(m)

    # 現場マーカー（赤い星）
    Marker(
        location=[lat, lng],
        popup=f"<b>{site_name}</b><br>{address}",
        icon=DivIcon(
            html='<div style="font-size:28px;color:red;text-shadow:1px 1px 2px rgba(0,0,0,0.5);transform:translate(-14px,-14px);">&#9733;</div>',
            icon_size=(30, 30),
            icon_anchor=(0, 0),
        ),
    ).add_to(m)

    # 現場ラベル（円の外側に配置）
    offset = _label_offset(radius_m)
    Marker(
        location=[lat + offset, lng],
        icon=DivIcon(
            html=f"""
            <div style="
                font-size: 11px; font-weight: bold;
                font-family: 'Yu Gothic', 'MS Gothic', sans-serif;
                color: #333; background: rgba(255,255,255,0.85);
                padding: 2px 6px; border: 1px solid #999;
                white-space: nowrap; transform: translateX(-50%);
            ">★ 工事現場（{address}）</div>
            """,
            icon_size=(200, 20),
            icon_anchor=(100, 10),
        ),
    ).add_to(m)

    # 一時ファイルに保存
    tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8")
    m.save(tmp.name)
    tmp.close()
    return tmp.name


def html_to_png(html_path, png_path, width=1200, height=900):
    """ヘッドレスChromeでHTMLをスクリーンショット→PNGに保存"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument(f"--window-size={width},{height}")
    options.add_argument("--hide-scrollbars")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(f"file:///{html_path.replace(os.sep, '/')}")
        # タイルの読み込みを待つ
        time.sleep(3)
        driver.save_screenshot(png_path)
    finally:
        driver.quit()
    return png_path


def generate_map_png(site_name, address, lat, lng, radius_m=50, output_dir=None, zoom_override=None, tile_name="Google Maps"):
    """地図HTMLを生成→PNGに変換して返す"""
    html_path = generate_map_html(site_name, address, lat, lng, radius_m, zoom_override=zoom_override, tile_name=tile_name)
    if output_dir is None:
        output_dir = tempfile.gettempdir()
    png_path = os.path.join(output_dir, "近隣説明範囲図.png")
    html_to_png(html_path, png_path)
    # 一時HTMLを削除
    os.unlink(html_path)
    return png_path
