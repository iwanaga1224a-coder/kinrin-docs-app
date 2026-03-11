# -*- coding: utf-8 -*-
"""近隣施設検索モジュール
OpenStreetMap Overpass API で範囲内の建物・施設を検索し、分類リストを作成
"""

import json
import urllib.request
import urllib.parse

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def _query_overpass(lat, lng, radius_m):
    """Overpass APIで範囲内のPOI（施設・建物）を取得"""
    query = f"""
    [out:json][timeout:15];
    (
      node["building"](around:{radius_m},{lat},{lng});
      way["building"](around:{radius_m},{lat},{lng});
      node["amenity"](around:{radius_m},{lat},{lng});
      way["amenity"](around:{radius_m},{lat},{lng});
      node["shop"](around:{radius_m},{lat},{lng});
      way["shop"](around:{radius_m},{lat},{lng});
      node["office"](around:{radius_m},{lat},{lng});
      way["office"](around:{radius_m},{lat},{lng});
      node["leisure"](around:{radius_m},{lat},{lng});
      way["leisure"](around:{radius_m},{lat},{lng});
      node["healthcare"](around:{radius_m},{lat},{lng});
      way["healthcare"](around:{radius_m},{lat},{lng});
    );
    out center tags;
    """
    data = urllib.parse.urlencode({"data": query}).encode("utf-8")
    req = urllib.request.Request(OVERPASS_URL, data=data, headers={"User-Agent": "kinrin-docs-app/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            return json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"Overpass APIエラー: {e}")
        return None


def _classify(tags):
    """OSMタグから施設の種別を判定"""
    building = tags.get("building", "")
    amenity = tags.get("amenity", "")
    healthcare = tags.get("healthcare", "")
    shop = tags.get("shop", "")
    leisure = tags.get("leisure", "")
    office = tags.get("office", "")

    # 病院・医療
    if amenity in ("hospital", "clinic", "doctors", "dentist", "pharmacy") or healthcare:
        return "医療施設"

    # 学校・教育
    if amenity in ("school", "kindergarten", "university", "college", "nursery", "childcare"):
        return "教育施設"

    # 保育・福祉
    if amenity in ("social_facility", "nursing_home", "community_centre"):
        return "福祉施設"

    # 宗教
    if amenity in ("place_of_worship",) or building in ("temple", "shrine", "church"):
        return "宗教施設"

    # 公園・レジャー
    if leisure or amenity == "park":
        return "公園・レジャー"

    # 店舗
    if shop:
        return "店舗・商業施設"

    # オフィス
    if office or building == "office" or building == "commercial":
        return "事務所・商業ビル"

    # 集合住宅
    if building in ("apartments", "residential", "dormitory"):
        return "集合住宅"

    # 戸建て
    if building in ("house", "detached", "terrace"):
        return "戸建て住宅"

    # その他の建物
    if building == "yes":
        return "建物（種別不明）"

    if building:
        return f"建物（{building}）"

    return "その他"


def search_nearby(lat, lng, radius_m):
    """範囲内の施設を検索し、種別ごとに分類して返す

    Returns:
        dict: {
            "種別名": [
                {"name": "施設名", "address": "住所", "category": "種別"},
                ...
            ]
        }
    """
    result = _query_overpass(lat, lng, radius_m)
    if not result or "elements" not in result:
        return {}

    classified = {}
    seen_names = set()  # 重複排除用

    for elem in result["elements"]:
        tags = elem.get("tags", {})
        if not tags:
            continue

        name = tags.get("name", "")
        addr = tags.get("addr:full", "") or tags.get("addr:street", "")
        housenumber = tags.get("addr:housenumber", "")
        if housenumber and addr:
            addr = f"{addr} {housenumber}"

        category = _classify(tags)

        # 名前がない建物は種別だけでカウント
        display_name = name if name else ""

        # 重複チェック（同じ名前の施設は1回だけ）
        dedup_key = f"{category}:{name}" if name else f"{category}:{elem.get('id', '')}"
        if dedup_key in seen_names:
            continue
        seen_names.add(dedup_key)

        if category not in classified:
            classified[category] = []

        classified[category].append({
            "name": display_name,
            "address": addr,
            "category": category,
        })

    return classified


def search_nearby_with_coords(lat, lng, radius_m):
    """範囲内の建物・施設を座標付きで取得（地図マッピング用）

    Returns:
        list: [
            {"no": 1, "lat": ..., "lng": ..., "name": "...", "category": "...", "address": "..."},
            ...
        ]
    """
    result = _query_overpass(lat, lng, radius_m)
    if not result or "elements" not in result:
        return []

    buildings = []
    seen = set()

    for elem in result["elements"]:
        tags = elem.get("tags", {})
        if not tags:
            continue

        # 座標を取得（nodeは直接、wayはcenter）
        if elem["type"] == "node":
            e_lat = elem.get("lat")
            e_lng = elem.get("lon")
        elif elem["type"] == "way" and "center" in elem:
            e_lat = elem["center"].get("lat")
            e_lng = elem["center"].get("lon")
        else:
            continue

        if e_lat is None or e_lng is None:
            continue

        # 重複排除
        dedup_key = f"{elem.get('id', '')}"
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        name = tags.get("name", "")
        addr = tags.get("addr:full", "") or tags.get("addr:street", "")
        housenumber = tags.get("addr:housenumber", "")
        if housenumber and addr:
            addr = f"{addr} {housenumber}"

        category = _classify(tags)

        buildings.append({
            "lat": e_lat,
            "lng": e_lng,
            "name": name,
            "category": category,
            "address": addr,
        })

    # 番号を振る（北→南、西→東の順でソート）
    buildings.sort(key=lambda b: (-b["lat"], b["lng"]))
    for i, b in enumerate(buildings):
        b["no"] = i + 1

    return buildings


def format_nearby_list(classified):
    """分類済みデータを見やすいテキストリストに変換"""
    if not classified:
        return "範囲内の施設情報を取得できませんでした。\n現地確認をお願いします。"

    # 優先表示順
    priority = [
        "医療施設", "教育施設", "福祉施設", "宗教施設",
        "集合住宅", "戸建て住宅",
        "店舗・商業施設", "事務所・商業ビル",
        "公園・レジャー",
    ]

    lines = []
    lines.append("【近隣説明範囲内の施設・建物一覧】\n")

    # 優先順で表示
    shown = set()
    for cat in priority:
        if cat in classified:
            _format_category(lines, cat, classified[cat])
            shown.add(cat)

    # 残りのカテゴリ
    for cat in sorted(classified.keys()):
        if cat not in shown:
            _format_category(lines, cat, classified[cat])

    lines.append("\n※ OpenStreetMapのデータに基づく参考情報です。")
    lines.append("※ 現地確認で正確な対象範囲を特定してください。")

    return "\n".join(lines)


def _format_category(lines, category, items):
    """カテゴリごとのフォーマット"""
    named = [i for i in items if i["name"]]
    unnamed_count = len(items) - len(named)

    lines.append(f"■ {category}")

    if named:
        for item in named:
            addr_part = f"（{item['address']}）" if item["address"] else ""
            lines.append(f"  - {item['name']}{addr_part}")

    if unnamed_count > 0:
        lines.append(f"  - 他 {unnamed_count}件（名称不明）")

    if not named and unnamed_count == 0:
        lines.append(f"  - {len(items)}件")

    lines.append("")
