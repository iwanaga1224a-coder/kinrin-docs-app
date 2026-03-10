# -*- coding: utf-8 -*-
"""住所ユーティリティ
- 住所 → 緯度経度（国土地理院API）
- 住所 → 区名の自動判定
"""

import json
import re
import urllib.request
import urllib.parse


def geocode(address):
    """住所から緯度経度を取得（国土地理院 ジオコーディングAPI）
    Returns: (lat, lng) or None
    """
    encoded = urllib.parse.quote(address)
    url = f"https://msearch.gsi.go.jp/address-search/AddressSearch?q={encoded}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "kinrin-docs-app/1.0"})
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode("utf-8"))
        if data:
            lng, lat = data[0]["geometry"]["coordinates"]
            return float(lat), float(lng)
    except Exception:
        pass
    return None


def extract_ward(address):
    """住所から区名を抽出
    例: '東京都新宿区西新宿2-8-1' → '新宿'
        '東京都世田谷区...' → '世田谷'
        '東京都八王子市...' → '八王子'（市の場合）
    """
    # 特別区
    m = re.search(r"(?:東京都)?(\S+?)区", address)
    if m:
        return m.group(1)
    # 市
    m = re.search(r"(?:東京都)?(\S+?)市", address)
    if m:
        return m.group(1)
    return ""


def extract_ward_with_suffix(address):
    """区名を「区」付きで返す
    例: '東京都新宿区西新宿2-8-1' → '新宿区'
    """
    m = re.search(r"(?:東京都)?(\S+?[区市])", address)
    if m:
        return m.group(1)
    return ""
