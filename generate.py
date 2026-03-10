# -*- coding: utf-8 -*-
"""近隣説明会 書類一括生成スクリプト

使い方:
  python generate.py

対話形式で必要情報を入力すると、以下の書類をまとめて生成します:
  1. 標識設置届（Word）
  2. 近隣説明報告書（Word）
  3. 工事のお知らせ（Word）
  4. 近隣説明範囲図（地図付きWord）
"""

import os
import sys
import json
from datetime import datetime

# 同じディレクトリのモジュールをインポート
sys.path.insert(0, os.path.dirname(__file__))
from map_generator import generate_map_png
from doc_generator import (
    generate_sign_notice,
    generate_explanation_report,
    generate_construction_notice,
    generate_map_document,
)


# ========== デモ用プリセット ==========

DEMO_DATA = {
    # 工事基本情報
    "site_name": "○○ビル解体工事",
    "site_address": "東京都新宿区西新宿2-8-1",
    "lat": 35.6896,
    "lng": 139.6917,
    "radius_m": 50,
    "work_content": "鉄筋コンクリート造建物の解体工事",
    "building_name": "○○ビル",
    "building_use": "事務所",

    # 建物情報
    "site_area": "500.00",
    "building_area": "350.00",
    "total_floor_area": "2,100.00",
    "structure": "鉄筋コンクリート造",
    "floors_above": "6",
    "floors_below": "1",
    "height": "22.5",

    # 工期
    "start_date": "令和8年5月1日",
    "end_date": "令和8年10月31日",
    "work_hours": "午前8時00分 ～ 午後5時00分",
    "holidays": "日曜日・祝日",

    # 届出情報
    "ward_name": "新宿",
    "submit_date": "令和8年3月10日",
    "sign_install_date": "令和8年3月10日",
    "sign_location": "建築予定地の道路に面する見やすい場所",

    # 届出者（建築主・発注者）
    "applicant_name": "株式会社 東都建設　代表取締役　東都 太郎",
    "applicant_address": "東京都千代田区千代田1-1-1",
    "applicant_tel": "03-0000-0001",
    "client_name": "株式会社 東都建設",

    # 設計者
    "designer_name": "○○設計事務所",
    "designer_tel": "03-0000-0002",

    # 施工者
    "constructor_name": "株式会社 新田総合建設",
    "constructor_tel": "03-1234-0000",
    "site_manager": "新田 顕大",

    # 説明実施情報
    "explanation_date": "令和8年3月15日",
    "explanation_method": "個別訪問による説明及び書面配布",
    "target_count": "25",
    "explained_count": "20",
    "unexplained_count": "5",
    "opinions": "特になし",
}


def ask_or_default(prompt, default=""):
    """ユーザーに入力を求め、空ならデフォルト値を返す"""
    display = f"{prompt} [{default}]: " if default else f"{prompt}: "
    value = input(display).strip()
    return value if value else default


def collect_data_interactive():
    """対話形式で工事情報を収集"""
    print("=" * 60)
    print("  近隣説明会 書類一括生成システム")
    print("  必要な情報を入力してください（Enterでデモ値を使用）")
    print("=" * 60)
    print()

    data = {}

    print("【工事基本情報】")
    data["site_name"] = ask_or_default("工事名称", DEMO_DATA["site_name"])
    data["site_address"] = ask_or_default("工事場所（住所）", DEMO_DATA["site_address"])
    data["lat"] = float(ask_or_default("緯度", str(DEMO_DATA["lat"])))
    data["lng"] = float(ask_or_default("経度", str(DEMO_DATA["lng"])))
    data["radius_m"] = int(ask_or_default("説明範囲（半径m）", str(DEMO_DATA["radius_m"])))
    data["work_content"] = ask_or_default("工事内容", DEMO_DATA["work_content"])
    print()

    print("【建物情報】")
    data["building_name"] = ask_or_default("建物名称", DEMO_DATA["building_name"])
    data["building_use"] = ask_or_default("用途", DEMO_DATA["building_use"])
    data["structure"] = ask_or_default("構造", DEMO_DATA["structure"])
    data["floors_above"] = ask_or_default("地上階数", DEMO_DATA["floors_above"])
    data["floors_below"] = ask_or_default("地下階数", DEMO_DATA["floors_below"])
    data["height"] = ask_or_default("高さ(m)", DEMO_DATA["height"])
    data["site_area"] = ask_or_default("敷地面積(㎡)", DEMO_DATA["site_area"])
    data["building_area"] = ask_or_default("建築面積(㎡)", DEMO_DATA["building_area"])
    data["total_floor_area"] = ask_or_default("延べ面積(㎡)", DEMO_DATA["total_floor_area"])
    print()

    print("【工期】")
    data["start_date"] = ask_or_default("着工予定日", DEMO_DATA["start_date"])
    data["end_date"] = ask_or_default("完了予定日", DEMO_DATA["end_date"])
    data["work_hours"] = ask_or_default("作業時間", DEMO_DATA["work_hours"])
    data["holidays"] = ask_or_default("休工日", DEMO_DATA["holidays"])
    print()

    print("【届出情報】")
    data["ward_name"] = ask_or_default("届出先の区名", DEMO_DATA["ward_name"])
    data["submit_date"] = ask_or_default("届出日", DEMO_DATA["submit_date"])
    data["sign_install_date"] = ask_or_default("標識設置日", DEMO_DATA["sign_install_date"])
    data["sign_location"] = DEMO_DATA["sign_location"]
    print()

    print("【届出者（建築主・発注者）】")
    data["applicant_name"] = ask_or_default("届出者 氏名", DEMO_DATA["applicant_name"])
    data["applicant_address"] = ask_or_default("届出者 住所", DEMO_DATA["applicant_address"])
    data["applicant_tel"] = ask_or_default("届出者 電話", DEMO_DATA["applicant_tel"])
    data["client_name"] = ask_or_default("発注者名", DEMO_DATA["client_name"])
    print()

    print("【設計者】")
    data["designer_name"] = ask_or_default("設計者名", DEMO_DATA["designer_name"])
    data["designer_tel"] = ask_or_default("設計者 電話", DEMO_DATA["designer_tel"])
    print()

    print("【施工者】")
    data["constructor_name"] = ask_or_default("施工者名", DEMO_DATA["constructor_name"])
    data["constructor_tel"] = ask_or_default("施工者 電話", DEMO_DATA["constructor_tel"])
    data["site_manager"] = ask_or_default("現場責任者", DEMO_DATA["site_manager"])
    print()

    print("【説明実施情報】")
    data["explanation_date"] = ask_or_default("説明実施日", DEMO_DATA["explanation_date"])
    data["explanation_method"] = ask_or_default("説明方法", DEMO_DATA["explanation_method"])
    data["target_count"] = ask_or_default("説明対象戸数", DEMO_DATA["target_count"])
    data["explained_count"] = ask_or_default("説明済み戸数", DEMO_DATA["explained_count"])
    data["unexplained_count"] = ask_or_default("未説明戸数", DEMO_DATA["unexplained_count"])
    data["opinions"] = ask_or_default("住民からの意見", DEMO_DATA["opinions"])
    print()

    return data


def generate_all(data, output_dir=None):
    """全書類を一括生成"""
    if output_dir is None:
        desktop = os.path.join(os.path.expanduser("~"), "OneDrive", "デスクトップ")
        if not os.path.exists(desktop):
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        safe_name = data["site_name"].replace("/", "_").replace("\\", "_")
        output_dir = os.path.join(desktop, f"近隣説明会_{safe_name}")

    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("  書類生成を開始します...")
    print(f"  出力先: {output_dir}")
    print("=" * 60)

    results = []

    # 1. 近隣説明範囲図（地図PNG）
    print("\n[1/4] 近隣説明範囲図を生成中...")
    map_png = generate_map_png(
        site_name=data["site_name"],
        address=data["site_address"],
        lat=data["lat"],
        lng=data["lng"],
        radius_m=data["radius_m"],
        output_dir=output_dir,
    )
    print(f"  → 地図PNG: {map_png}")

    # 1b. 地図Word
    map_docx_path = os.path.join(output_dir, "01_近隣説明範囲図.docx")
    generate_map_document(data, map_png, map_docx_path)
    results.append(("近隣説明範囲図", map_docx_path))
    print(f"  → Word: {map_docx_path}")

    # 2. 標識設置届
    print("\n[2/4] 標識設置届を生成中...")
    sign_path = os.path.join(output_dir, "02_標識設置届.docx")
    generate_sign_notice(data, sign_path)
    results.append(("標識設置届", sign_path))
    print(f"  → {sign_path}")

    # 3. 近隣説明報告書
    print("\n[3/4] 近隣説明報告書を生成中...")
    report_path = os.path.join(output_dir, "03_近隣説明報告書.docx")
    generate_explanation_report(data, report_path)
    results.append(("近隣説明報告書", report_path))
    print(f"  → {report_path}")

    # 4. 工事のお知らせ
    print("\n[4/4] 工事のお知らせを生成中...")
    notice_path = os.path.join(output_dir, "04_工事のお知らせ.docx")
    generate_construction_notice(data, notice_path)
    results.append(("工事のお知らせ", notice_path))
    print(f"  → {notice_path}")

    # 入力データをJSONで保存（再利用・テンプレート化用）
    json_path = os.path.join(output_dir, "入力データ.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("  生成完了！")
    print("=" * 60)
    for name, path in results:
        print(f"  [OK] {name}: {os.path.basename(path)}")
    print(f"  [OK] 入力データ: 入力データ.json")
    print(f"\n  出力フォルダ: {output_dir}")
    print("=" * 60)

    return output_dir, results


def generate_from_dict(data_dict, output_dir=None):
    """辞書データから直接生成（Claude連携用）"""
    merged = {**DEMO_DATA, **data_dict}
    return generate_all(merged, output_dir)


# ========== エントリーポイント ==========

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # デモモード: 全項目デモデータで即生成
        print("デモモードで実行します...")
        generate_all(DEMO_DATA)
    elif len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        # JSONファイルから読み込み
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = {**DEMO_DATA, **data}
        generate_all(merged)
    else:
        # 対話モード
        data = collect_data_interactive()
        generate_all(data)
