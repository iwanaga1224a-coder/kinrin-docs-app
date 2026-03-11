# -*- coding: utf-8 -*-
"""自治体ごとの条例・様式設定

各自治体の中高層建築物条例に基づく標識設置届・近隣説明報告書の
条例名・条文番号・宛先・届出要件を管理する。

※ 条例名・条文番号は2026年3月時点の調査に基づく（SOURCES.md参照）。
   実務では必ず管轄窓口で最新の様式を確認してください。
"""

# デフォルト（東京都条例ベース）
_DEFAULT = {
    "suffix": "区長",
    "ordinance_name": "東京都中高層建築物の建築に係る紛争の予防と調整に関する条例",
    "sign_article": "第6条",
    "explanation_article": "第7条",
    "note": "",
    "height_threshold": "10m超（第1種低層住居専用地域では軒高7m超又は3階以上）",
    "sign_period": "",
}

# ========== 23区 ==========
WARD_CONFIG = {
    "千代田": {
        "suffix": "区長",
        "ordinance_name": "千代田区中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第5条",
        "explanation_article": "第6条",
        "note": "確認申請の15日前（延べ1,000m2超かつ高さ15m超は30日前）。別途「建築計画の早期周知に関する条例」あり（20m超等は60日前）",
        "height_threshold": "10m超",
        "sign_period": "15日前/30日前（規模別）",
        "regulation_url": "https://www.city.chiyoda.lg.jp/koho/machizukuri/kenchiku/jizentetsuzuki/chukoso.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 30,
            "sign_deadline_other": 30,
            "requires_submission": True,
            "form_note": "標識設置後1週間以内に報告書を提出",
        },
    },
    "中央": {
        "suffix": "区長",
        "ordinance_name": "中央区中高層建築物の建築計画の事前公開等に関する指導要綱",
        "sign_article": "第4条",
        "explanation_article": "第5条",
        "note": "条例ではなく指導要綱。標識設置期間: 確認申請の60日前（延べ1,000m2以下かつ高さ30m以下=30日前、延べ500m2以下かつ高さ15m以下=15日前）",
        "height_threshold": "10m超",
        "sign_period": "15日前/30日前/60日前（規模別）",
        "uses_metro_ordinance": True,
        "regulation_url": "https://www.city.chuo.lg.jp/a0043/machizukuri/kenchiku/kentikutetuzuki/tyuukousou_youkou.html",
        "demolition": {
            "target_area": 0,
            "sign_deadline_wood": 15,
            "sign_deadline_other": 30,
            "requires_submission": True,
            "form_note": "解体工事計画の事前周知届を提出",
        },
    },
    "港": {
        "suffix": "区長",
        "ordinance_name": "港区中高層建築物等の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第6条",
        "explanation_article": "第7条",
        "note": "",
        "height_threshold": "10m超（1低・2低では軒高7m超又は3階以上）",
        "sign_period": "",
        "regulation_url": "https://www.city.minato.tokyo.jp/kenchikufunsou/kennchikufunnsouchoouseitantou/tyuukousou1.html",
        "demolition": {
            "target_area": 0,
            "sign_deadline_wood": 15,
            "sign_deadline_other": 30,
            "requires_submission": True,
            "form_note": "解体工事の標識設置届・説明報告書を提出",
        },
    },
    "新宿": {
        "suffix": "区長",
        "ordinance_name": "新宿区中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第5条第2項",
        "explanation_article": "第6条",
        "note": "標識設置後5日以内に届出（土日祝含む）",
        "height_threshold": "10m超又は4階以上（1低・2低・田園住居では軒高7m超又は3階以上）",
        "sign_period": "設置後5日以内に届出",
        "regulation_url": "https://www.city.shinjuku.lg.jp/seikatsu/file18_04_00003.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 15,
            "sign_deadline_other": 30,
            "requires_submission": True,
            "form_note": "解体工事の事前周知届出書を提出",
        },
    },
    "文京": {
        "suffix": "区長",
        "ordinance_name": "文京区中高層建築物の建築に係る紛争の予防と調整及び開発事業の周知に関する条例",
        "sign_article": "第6条",
        "explanation_article": "第7条",
        "note": "標識設置後4日以内に届出（土日含む）。開発事業の周知も同条例に含む",
        "height_threshold": "10m超（1低層では軒高7m超又は3階以上）",
        "sign_period": "設置後4日以内に届出（設置期間: 15日前/30日前/60日前 規模別）",
        "regulation_url": "https://www.city.bunkyo.lg.jp/b032/p004750.html",
        "demolition": {
            "target_area": 0,
            "sign_deadline_wood": 15,
            "sign_deadline_other": 30,
            "requires_submission": True,
            "form_note": "解体工事届出書を工事15日前までに提出",
        },
    },
    "台東": {
        "suffix": "区長",
        "ordinance_name": "東京都台東区中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第6条",
        "explanation_article": "第8条",
        "note": "正式名称に「東京都」を含む。特定中高層=15m超。収容台数20台以上の立体駐車場も対象。標識設置後7日以内に届出",
        "height_threshold": "10m超（特定中高層=15m超）",
        "sign_period": "設置後7日以内に届出",
        "regulation_url": "https://www.city.taito.lg.jp/kenchiku/jutaku/sumai/funso/yobo.html",
        "demolition": {
            "target_area": 0,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 14,
            "requires_submission": True,
            "form_note": "工事7日前までに報告書を提出",
        },
    },
    "墨田": {
        "suffix": "区長",
        "ordinance_name": "墨田区中高層建築物の建築に係る紛争の予防及び調整に関する条例",
        "sign_article": "第5条",
        "explanation_article": "第6条",
        "note": "標識設置期間が規模別3段階: 通常15日前、特定中高層30日前、特別特定中高層60日前",
        "height_threshold": "10m超",
        "sign_period": "15日前/30日前/60日前（規模別）",
        "regulation_url": "https://www.city.sumida.lg.jp/matizukuri/kentiku/keikaku/cyuukouosu.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": True,
            "form_note": "工事7日前までに報告書を提出",
        },
    },
    "江東": {
        "suffix": "区長",
        "ordinance_name": "江東区中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第5条",
        "explanation_article": "第6条",
        "note": "",
        "height_threshold": "10m超",
        "sign_period": "",
        "regulation_url": "https://www.city.koto.lg.jp/395108/machizukuri/kenchiku/tatemono/hunso/7184.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 14,
            "requires_submission": True,
            "form_note": "工事7日前までに届出書を提出",
        },
    },
    "品川": {
        "suffix": "区長",
        "ordinance_name": "品川区中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第6条",
        "explanation_article": "第7条",
        "note": "",
        "height_threshold": "10m超（1低・2低で軒高7m超又は3階以上、その他で4階以上）",
        "sign_period": "",
        "regulation_url": "http://www.city.shinagawa.tokyo.jp/PC/kankyo/kankyo-toshiseibi/kankyo-toshiseibi-hunnsouyobou/hpg000016196.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 10,
            "sign_deadline_other": 14,
            "requires_submission": True,
            "form_note": "標識設置届＋説明報告書を提出",
        },
    },
    "目黒": {
        "suffix": "区長",
        "ordinance_name": "目黒区中高層建築物等の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第5条",
        "explanation_article": "第6条",
        "note": "大規模建築物（延べ1,500㎡以上かつ高さ15m以上等）も対象",
        "height_threshold": "10m超（1低層で軒高7m超又は3階以上）",
        "sign_period": "30日前/60日前/90日前（規模別）",
        "regulation_url": "https://www.city.meguro.tokyo.jp/toshikeikaku/shigoto/kenchiku/hyoshiki.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 15,
            "sign_deadline_other": 15,
            "requires_submission": True,
            "form_note": "工事5日前までに届出書を提出",
        },
    },
    "大田": {
        "suffix": "区長",
        "ordinance_name": "大田区中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第5条",
        "explanation_article": "第6条",
        "note": "",
        "height_threshold": "10m超（1低層・2低層では軒高7m超又は3階以上）",
        "sign_period": "",
        "regulation_url": "https://www.city.ota.tokyo.jp/seikatsu/sumaimachinami/kenchiku/chuukousou_seido/hyousikisetumei.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 10,
            "sign_deadline_other": 10,
            "requires_submission": True,
            "form_note": "500m²以上等は報告書必要",
        },
    },
    "世田谷": {
        "suffix": "区長",
        "ordinance_name": "世田谷区中高層建築物等の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第6条",
        "explanation_article": "第7条",
        "note": "1低・2低で高さ8m又は軒高7m超も対象（独自基準）",
        "height_threshold": "10m超（1低・2低で高さ8m又は軒高7m超、商業系以外で3階以上）",
        "sign_period": "",
        "regulation_url": "https://www.city.setagaya.lg.jp/02034/3773.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": True,
            "form_note": "建リ法届出に記載で報告書省略可（R7.4.1〜）",
        },
    },
    "渋谷": {
        "suffix": "区長",
        "ordinance_name": "渋谷区中高層建築物等の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第6条",
        "explanation_article": "第7条",
        "note": "令和7年4月1日改正あり",
        "height_threshold": "10m超（1低・2低では軒高7m超又は3階以上）",
        "sign_period": "",
        "regulation_url": "https://www.city.shibuya.tokyo.jp/kankyo/kenchiku/kenchiku-jorei/hunsou.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 30,
            "sign_deadline_other": 30,
            "requires_submission": True,
            "form_note": "条例に基づく標識設置届＋説明報告書を提出",
        },
    },
    "中野": {
        "suffix": "区長",
        "ordinance_name": "中野区中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第5条",
        "explanation_article": "第6条",
        "note": "標識設置後5日以内に届出",
        "height_threshold": "10m超（低層住居専用地域では軒高7m超又は3階以上）",
        "sign_period": "設置後5日以内に届出",
        "regulation_url": "https://www.city.tokyo-nakano.lg.jp/machizukuri/kenchiku/tetsuzuki/kenchikufunso/kenchikufunso.html",
        "demolition": {
            "target_area": 0,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": True,
            "form_note": "80m²以上は建リ法届出に写真添付、80m²未満は別途届出",
        },
    },
    "杉並": {
        "suffix": "区長",
        "ordinance_name": "杉並区中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第6条",
        "explanation_article": "第7条（推定）",
        "note": "標識設置=第6条は標識設置届PDF（第2号様式）で確認済み。説明義務の条文番号は例規集(D1-Law)で直接確認できていない（第7条又は第8条推定）。商業地域以外で3階以上も対象",
        "height_threshold": "10m超（低層住居専用地域では軒高7m超又は3階以上、商業地域以外で3階以上も対象）",
        "sign_period": "",
        "regulation_url": "https://www.city.suginami.tokyo.jp/s092/1890.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": True,
            "form_note": "工事7日前までに届出書を提出",
        },
    },
    "豊島": {
        "suffix": "区長",
        "ordinance_name": "豊島区中高層建築物の建築に係る紛争の予防及び調整に関する条例",
        "sign_article": "第5条",
        "explanation_article": "第6条",
        "note": "",
        "height_threshold": "10m超（1低層では軒高7m超又は3階以上）",
        "sign_period": "",
        "regulation_url": "https://www.city.toshima.lg.jp/314/machizukuri/sumai/kekaku/tateru/013325.html",
        "demolition": {
            "target_area": 0,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "R6年度〜届出不要（掲示のみ必要）",
        },
    },
    "北": {
        "suffix": "区長",
        "ordinance_name": "東京都北区中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第5条",
        "explanation_article": "第6条",
        "note": "正式名称に「東京都」を含む",
        "height_threshold": "10m超（2低層では軒高7m超又は3階以上）",
        "sign_period": "",
        "regulation_url": "https://www.city.kita.lg.jp/dev-environment/construction/1018294/1009335.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 15,
            "sign_deadline_other": 30,
            "requires_submission": True,
            "form_note": "工事7日前までに届出書を提出",
        },
    },
    "荒川": {
        "suffix": "区長",
        "ordinance_name": "荒川区中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第5条",
        "explanation_article": "第6条",
        "note": "標識設置後7日以内に届出。未設置時の公表規定あり（第15条）",
        "height_threshold": "10m超（低層住居専用地域では軒高7m超又は3階以上）",
        "sign_period": "設置後7日以内に届出",
        "regulation_url": "https://www.city.arakawa.tokyo.jp/a041/machizukuridoboku/kenchikukaihatsu/funnsoujourei.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 14,
            "requires_submission": True,
            "form_note": "標識設置後翌日から木造3日以内・非木造7日以内に報告",
        },
    },
    "板橋": {
        "suffix": "区長",
        "ordinance_name": "東京都板橋区中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第4条",
        "explanation_article": "第5条（推定）",
        "note": "正式名称に「東京都」を含む。標識設置=第4条第1項(設置義務)・第4条第2項(届出義務)は手引きPDF（令和7年2月版）で確認済み。説明義務は第5条推定（例規集D1-Lawで直接確認できていない）。延べ2,000m2超かつ高さ20m超は説明会義務（大規模建築物指導要綱の可能性あり）",
        "height_threshold": "10m超（1低層で軒高7m超又は3階以上）",
        "sign_period": "確認申請の60日前",
        "regulation_url": "https://www.city.itabashi.tokyo.jp/bousai/tochi/jorei/1006203.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": True,
            "form_note": "建リ法届出時に済シール交付",
        },
    },
    "練馬": {
        "suffix": "区長",
        "ordinance_name": "練馬区中高層建築物等の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第5条",
        "explanation_article": "第6条",
        "note": "第7条は了解取得努力義務。1低・2低・田園住居地域では8m超（他区の7mと異なる独自基準）",
        "height_threshold": "10m超（1低・2低・田園住居地域では8m超）",
        "sign_period": "",
        "regulation_url": "https://www.city.nerima.tokyo.jp/jigyoshamuke/jigyosha/doboku/yobo.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 14,
            "sign_deadline_other": 14,
            "requires_submission": True,
            "form_note": "アスベスト飛散防止条例に基づく届出",
        },
    },
    "足立": {
        "suffix": "区長",
        "ordinance_name": "足立区中高層建築物等の建築に係る紛争の予防及び調整条例",
        "sign_article": "第5条",
        "explanation_article": "第8条",
        "note": "標識届出期限: 設置後7日以内。標識設置期間: 一戸建て15日前/集合住宅等30日前（確認申請前）。特定中高層=20m超",
        "height_threshold": "10m超（低層住居専用地域では軒高7m超、特定中高層=20m超）",
        "sign_period": "設置後7日以内に届出（設置期間: 一戸建て15日前/集合住宅等30日前）",
        "regulation_url": "https://www.city.adachi.tokyo.jp/k-shinsa/machi/kaihatsushido/funso.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": True,
            "form_note": "規模による（500m²以上等は報告書必要）",
        },
    },
    "葛飾": {
        "suffix": "区長",
        "ordinance_name": "葛飾区中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第5条",
        "explanation_article": "第6条",
        "note": "標識設置後7日以内に届出",
        "height_threshold": "10m超（低層住居専用地域では軒高7m超又は3階以上）",
        "sign_period": "設置後7日以内に届出",
        "regulation_url": "https://www.city.katsushika.lg.jp/business/1000011/1000069/1005250/1005333.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": True,
            "form_note": "周知終了後すみやかに報告書を提出",
        },
    },
    "江戸川": {
        "suffix": "区長",
        "ordinance_name": "江戸川区中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第5条",
        "explanation_article": "第6条",
        "note": "標識設置後速やかに届出",
        "height_threshold": "10m超（1低層で軒高7m超又は3階以上）",
        "sign_period": "速やかに届出",
        "regulation_url": "https://www.city.edogawa.tokyo.jp/e016/toshikeikaku/kenchiku/ruletokyogi/funsoujorei.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": True,
            "form_note": "事前周知届出書を提出",
        },
    },

    # ========== 多摩地域（独自条例あり） ==========
    "八王子": {
        "suffix": "市長",
        "ordinance_name": "八王子市中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第5条",
        "explanation_article": "第6条",
        "note": "",
        "height_threshold": "10m超（1低・2低では軒高7m超又は3階以上）",
        "sign_period": "",
        "regulation_url": "https://www.city.hachioji.tokyo.jp/jigyosha/005/10101/p021517.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "建設リサイクル法に基づく届出のみ（独自の解体事前周知制度なし）",
        },
    },
    "立川": {
        "suffix": "市長",
        "ordinance_name": "立川市中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第5条",
        "explanation_article": "第6条",
        "note": "※条文番号はPDF確認による推定。施行規則第5条(設置時期)・第7条(届出)・第9条(説明方法)で詳細規定",
        "height_threshold": "10m超（1低・2低では軒高7m超又は3階以上）",
        "sign_period": "",
        "regulation_url": "https://www.city.tachikawa.lg.jp/shisei/machizukuri/1006749/1006798/1006805/1006819.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "建設リサイクル法に基づく届出のみ（独自の解体事前周知制度なし）",
        },
    },
    "武蔵野": {
        "suffix": "市長",
        "ordinance_name": "武蔵野市まちづくり条例",
        "sign_article": "まちづくり条例内",
        "explanation_article": "まちづくり条例内",
        "note": "独自の紛争予防条例はなく、まちづくり条例で標識設置・説明義務を包括。紛争調整は別条例（武蔵野市中高層建築物の建築に係る紛争の調整に関する条例）",
        "height_threshold": "10m超（低層住居専用地域では軒高7m超又は3階以上）",
        "sign_period": "",
        "regulation_url": "https://www.city.musashino.lg.jp/kurashi_tetsuzuki/machizukuri/machizukurijorei/1008495.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "建設リサイクル法に基づく届出のみ（独自の解体事前周知制度なし）",
        },
    },
    "三鷹": {
        "suffix": "市長",
        "ordinance_name": "三鷹市まちづくり条例",
        "sign_article": "第27条",
        "explanation_article": "第28条",
        "note": "独自の紛争予防条例はなく、まちづくり条例で包括。紛争調整は別条例（三鷹市開発事業に係る紛争の調整に関する条例）",
        "height_threshold": "10m超（低層住居専用地域では軒高7m超又は3階以上）",
        "sign_period": "",
        "regulation_url": "https://www.city.mitaka.lg.jp/c_service/003/003111.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "建設リサイクル法に基づく届出のみ（独自の解体事前周知制度なし）",
        },
    },
    "府中": {
        "suffix": "市長",
        "ordinance_name": "府中市中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第6条",
        "explanation_article": "第7条",
        "note": "標識設置日から3日以内に届出",
        "height_threshold": "10m超（1低・2低では軒高7m超又は3階以上）",
        "sign_period": "設置後3日以内に届出",
        "regulation_url": "https://www.city.fuchu.tokyo.jp/gyosei/hosin/jyorei/funso.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "建設リサイクル法に基づく届出のみ（独自の解体事前周知制度なし）",
        },
    },
    "調布": {
        "suffix": "市長",
        "ordinance_name": "中高層建築物の建築に係る紛争の予防と調整に関する条例（調布市）",
        "sign_article": "条例に規定（条文番号要確認）",
        "explanation_article": "条例に規定（条文番号要確認）",
        "note": "※条文番号は手引きPDFで確認要。「ほっとするふるさとをはぐくむ街づくり条例」との二本立て。建築指導課 042-481-7512",
        "height_threshold": "10m超（1低・2低・田園住居では軒高7m超又は3階以上）",
        "sign_period": "",
        "regulation_url": "https://www.city.chofu.lg.jp/080080/p051012.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "建設リサイクル法に基づく届出のみ（独自の解体事前周知制度なし）",
        },
    },
    "町田": {
        "suffix": "市長",
        "ordinance_name": "町田市中高層建築物等の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "条例に規定（条文番号要確認）",
        "explanation_article": "条例に規定（条文番号要確認）",
        "note": "※条文番号は例規集で確認要。一戸建て住宅は対象外。集合住宅9戸以上・延べ1,000m2超も対象。確認申請20日前に標識設置、5日以内に届出",
        "height_threshold": "10m超（低層住居専用地域では軒高7m超又は3階以上）。集合住宅9戸以上・延べ1,000m2超も対象",
        "sign_period": "確認申請の20日前（設置後5日以内に届出）",
        "regulation_url": "https://www.city.machida.tokyo.jp/kurashi/sumai/toshikei/t_01/zizenkyogi/funsouyobou.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "建設リサイクル法に基づく届出のみ（独自の解体事前周知制度なし）",
        },
    },
    "日野": {
        "suffix": "市長",
        "ordinance_name": "日野市中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第5条",
        "explanation_article": "第6条",
        "note": "",
        "height_threshold": "10m超（低層住居専用地域では軒高7m超又は3階以上）",
        "sign_period": "",
        "regulation_url": "https://www.city.hino.lg.jp/shisei/machidukuri/kenchiku/1011311/1012077.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "建設リサイクル法に基づく届出のみ（独自の解体事前周知制度なし）",
        },
    },
    "国分寺": {
        "suffix": "市長",
        "ordinance_name": "国分寺市まちづくり条例",
        "sign_article": "第42条第2項",
        "explanation_article": "第42条第4項",
        "note": "まちづくり条例で中高層建築物を包括。開発基本計画届出後7日以内に標識設置、標識設置後14日以内に近隣説明。10m以下の一戸建ては対象外",
        "height_threshold": "10m超又は3階以上（一戸建て住宅を除く）",
        "sign_period": "届出後7日以内に標識設置、設置後14日以内に説明",
        "regulation_url": "https://www.city.kokubunji.tokyo.jp/kurashi/koutsuu/jourei/1002248.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "建設リサイクル法に基づく届出のみ（独自の解体事前周知制度なし）",
        },
    },
    "西東京": {
        "suffix": "市長",
        "ordinance_name": "西東京市中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第5条",
        "explanation_article": "第6条",
        "note": "※条文番号は推定（例規集DB直接アクセス不可のため）。施行規則で標識設置届=様式第2号、説明会等報告書=様式第4号を確認済み",
        "height_threshold": "10m超（低層住居専用地域では軒高7m超又は3階以上）",
        "sign_period": "",
        "regulation_url": "https://www.city.nishitokyo.lg.jp/kurasi/sinseisyo/itiran/kenchiku_etc/71117820170322160507133.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "建設リサイクル法に基づく届出のみ（独自の解体事前周知制度なし）",
        },
    },
    "小平": {
        "suffix": "市長",
        "ordinance_name": "小平市中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "条例に規定（条文番号要確認）",
        "explanation_article": "条例に規定（条文番号要確認）",
        "note": "※条文番号は手引きPDFで確認要。標識設置後3日以内に届出。1,000m2超かつ15m以上=申請30日前、その他=15日前に設置。説明会等報告書は確認申請10日前までに提出",
        "height_threshold": "10m超（低層住居専用地域では軒高7m超又は3階以上）",
        "sign_period": "設置後3日以内に届出（設置期間: 15日前/30日前 規模別）",
        "regulation_url": "https://www.city.kodaira.tokyo.jp/kurashi/086/086844.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "建設リサイクル法に基づく届出のみ（独自の解体事前周知制度なし）",
        },
    },
    "多摩": {
        "suffix": "市長",
        "ordinance_name": "多摩市街づくり条例",
        "sign_article": "第43条",
        "explanation_article": "第45条・第46条",
        "note": "街づくり条例で包括。第43条=標識設置・届出、第45条=縦覧・公告、第46条=住民意見書（公告日から14日以内）。大規模開発は第62条・第63条・第65条",
        "height_threshold": "10m超、又は10戸以上の共同住宅",
        "sign_period": "",
        "regulation_url": "https://www.city.tama.lg.jp/kurashi/machi/machidukuri/jorei/1005020.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "建設リサイクル法に基づく届出のみ（独自の解体事前周知制度なし）",
        },
    },
    "青梅": {
        "suffix": "市長",
        "ordinance_name": "東京都中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第6条",
        "explanation_article": "第7条",
        "note": "独自条例なし。東京都条例を適用。窓口: 東京都多摩建築指導事務所。別途「青梅市開発行為等の基準および手続に関する条例」あり",
        "height_threshold": "10m超（第1種低層住居専用地域では軒高7m超又は3階以上）",
        "sign_period": "",
        "uses_metro_ordinance": True,
        "regulation_url": "https://www.city.ome.tokyo.jp/soshiki/41/287.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "建設リサイクル法に基づく届出のみ（独自の解体事前周知制度なし）",
        },
    },
    "昭島": {
        "suffix": "市長",
        "ordinance_name": "東京都中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第6条",
        "explanation_article": "第7条",
        "note": "独自条例なし。東京都条例を適用。窓口: 東京都多摩建築指導事務所。別途「昭島市宅地開発等指導要綱」あり",
        "height_threshold": "10m超（第1種低層住居専用地域では軒高7m超又は3階以上）",
        "sign_period": "",
        "uses_metro_ordinance": True,
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "建設リサイクル法に基づく届出のみ（独自の解体事前周知制度なし）",
        },
    },
    "小金井": {
        "suffix": "市長",
        "ordinance_name": "東京都中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第6条",
        "explanation_article": "第7条",
        "note": "独自紛争予防条例なし（東京都条例適用）。窓口: 多摩建築指導事務所。別途「小金井市まちづくり条例」第37条で中高層建築物の事前手続きを規定（標識設置届=様式第33号、説明報告書を提出）",
        "height_threshold": "10m超（低層住居専用地域では軒高7m超又は3階以上）",
        "sign_period": "",
        "uses_metro_ordinance": True,
        "regulation_url": "https://www.city.koganei.lg.jp/shisei/seisakukeikaku/machitoshi/machizukuri/chuukousouyousiki.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "建設リサイクル法に基づく届出のみ（独自の解体事前周知制度なし）",
        },
    },
    "東村山": {
        "suffix": "市長",
        "ordinance_name": "東京都中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第6条",
        "explanation_article": "第7条",
        "note": "独自紛争予防条例なし（東京都条例適用）。窓口: 多摩建築指導事務所。別途「東村山市宅地開発及び建築物の建築に関する指導要綱」で事前協議・周知が必要（10m以上、16戸以上）",
        "height_threshold": "10m超（第1種低層住居専用地域では軒高7m超又は3階以上）",
        "sign_period": "",
        "uses_metro_ordinance": True,
        "regulation_url": "https://www.city.higashimurayama.tokyo.jp/shisei/machi/takuchi/kaihatu.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "建設リサイクル法に基づく届出のみ（独自の解体事前周知制度なし）",
        },
    },
    "国立": {
        "suffix": "市長",
        "ordinance_name": "東京都中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第6条",
        "explanation_article": "第7条",
        "note": "独自紛争予防条例なし（東京都条例適用）。窓口: 多摩建築指導事務所。別途「国立市まちづくり条例」で事前調整制度あり。景観条例との併用あり",
        "height_threshold": "10m超（第1種低層住居専用地域では軒高7m超又は3階以上）",
        "sign_period": "",
        "uses_metro_ordinance": True,
        "regulation_url": "https://www.city.kunitachi.tokyo.jp/machi/keikaku/9355.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "建設リサイクル法に基づく届出のみ（独自の解体事前周知制度なし）",
        },
    },
    "福生": {
        "suffix": "市長",
        "ordinance_name": "東京都中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第6条",
        "explanation_article": "第7条",
        "note": "独自紛争予防条例なし（東京都条例適用）。窓口: 多摩建築指導事務所。別途「福生市宅地開発等指導要綱」「福生市まちづくり景観条例」あり",
        "height_threshold": "10m超（第1種低層住居専用地域では軒高7m超又は3階以上）",
        "sign_period": "",
        "uses_metro_ordinance": True,
        "regulation_url": "https://www.city.fussa.tokyo.jp/municipal/cityplan/inquiry/1003594.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "建設リサイクル法に基づく届出のみ（独自の解体事前周知制度なし）",
        },
    },
    "狛江": {
        "suffix": "市長",
        "ordinance_name": "東京都中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第6条",
        "explanation_article": "第7条",
        "note": "独自紛争予防条例なし（東京都条例適用）。窓口: 多摩建築指導事務所。別途「狛江市まちづくり条例」で標識設置(第35条)・説明会(第37条)を規定",
        "height_threshold": "10m超（第1種低層住居専用地域では軒高7m超又は3階以上）",
        "sign_period": "",
        "uses_metro_ordinance": True,
        "regulation_url": "https://www.city.komae.tokyo.jp/index.cfm/41,4630,315,html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "建設リサイクル法に基づく届出のみ（独自の解体事前周知制度なし）",
        },
    },
    "東大和": {
        "suffix": "市長",
        "ordinance_name": "東京都中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第6条",
        "explanation_article": "第7条",
        "note": "独自紛争予防条例なし（東京都条例適用）。窓口: 多摩建築指導事務所。別途「東大和市街づくり条例」で近隣区域（境界線から20mと建物高さの2倍のいずれか長い方）への対応が必要",
        "height_threshold": "10m超（第1種低層住居専用地域では軒高7m超又は3階以上）",
        "sign_period": "",
        "uses_metro_ordinance": True,
        "regulation_url": "https://www.city.higashiyamato.lg.jp/reiki/reiki_honbun/g144RG00000760.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "建設リサイクル法に基づく届出のみ（独自の解体事前周知制度なし）",
        },
    },
    "清瀬": {
        "suffix": "市長",
        "ordinance_name": "東京都中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第6条",
        "explanation_article": "第7条",
        "note": "独自紛争予防条例なし（東京都条例適用）。窓口: 多摩建築指導事務所。別途「清瀬市住環境の整備に関する条例」第57〜59条で中高層建築物（10m超・16戸以上・延べ300m2以上ワンルーム）の標識設置・説明会義務を規定",
        "height_threshold": "10m超（第1種低層住居専用地域では軒高7m超又は3階以上）",
        "sign_period": "",
        "uses_metro_ordinance": True,
        "regulation_url": "https://www.city.kiyose.lg.jp/siseijouhou/machizukuri/kaihatu/1004482.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "建設リサイクル法に基づく届出のみ（独自の解体事前周知制度なし）",
        },
    },
    "東久留米": {
        "suffix": "市長",
        "ordinance_name": "東京都中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第6条",
        "explanation_article": "第7条",
        "note": "独自紛争予防条例なし（東京都条例適用）。窓口: 多摩建築指導事務所。別途「東久留米市宅地開発等に関する条例」で10m超・20戸以上の標識設置(様式第1号)・届出(様式第2号)・説明会を規定。標識設置: 事前協議申請書提出の15日前〜工事完了届提出日まで",
        "height_threshold": "10m超（第1種低層住居専用地域では軒高7m超又は3階以上）",
        "sign_period": "",
        "uses_metro_ordinance": True,
        "regulation_url": "https://www.city.higashikurume.lg.jp/shisei/sesaku/toshi/takuchi/1002424.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "建設リサイクル法に基づく届出のみ（独自の解体事前周知制度なし）",
        },
    },
    "武蔵村山": {
        "suffix": "市長",
        "ordinance_name": "東京都中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第6条",
        "explanation_article": "第7条",
        "note": "独自紛争予防条例なし（東京都条例適用）。窓口: 多摩建築指導事務所",
        "height_threshold": "10m超（第1種低層住居専用地域では軒高7m超又は3階以上）",
        "sign_period": "",
        "uses_metro_ordinance": True,
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "建設リサイクル法に基づく届出のみ（独自の解体事前周知制度なし）",
        },
    },
    "稲城": {
        "suffix": "市長",
        "ordinance_name": "東京都中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第6条",
        "explanation_article": "第7条",
        "note": "独自紛争予防条例なし（東京都条例適用）。窓口: 多摩建築指導事務所。別途「稲城市宅地開発等指導要綱」（10m超・15戸以上対象）と「稲城市中高層建築物の高さの最高限度に関する指導指針」あり",
        "height_threshold": "10m超（第1種低層住居専用地域では軒高7m超又は3階以上）",
        "sign_period": "",
        "uses_metro_ordinance": True,
        "regulation_url": "https://www.city.inagi.tokyo.jp/kankyo/machi_zukuri/1009069/1009070.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "建設リサイクル法に基づく届出のみ（独自の解体事前周知制度なし）",
        },
    },
    "羽村": {
        "suffix": "市長",
        "ordinance_name": "東京都中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第6条",
        "explanation_article": "第7条",
        "note": "独自紛争予防条例なし（東京都条例適用）。窓口: 多摩建築指導事務所",
        "height_threshold": "10m超（第1種低層住居専用地域では軒高7m超又は3階以上）",
        "sign_period": "",
        "uses_metro_ordinance": True,
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "建設リサイクル法に基づく届出のみ（独自の解体事前周知制度なし）",
        },
    },
    "あきる野": {
        "suffix": "市長",
        "ordinance_name": "東京都中高層建築物の建築に係る紛争の予防と調整に関する条例",
        "sign_article": "第6条",
        "explanation_article": "第7条",
        "note": "独自紛争予防条例なし（東京都条例適用）。窓口: 多摩建築指導事務所。別途「あきる野市宅地開発等指導要綱」で3階以上/10m超の標識設置・説明義務を規定。確認申請前に市との事前協議・承認が必要",
        "height_threshold": "10m超（1低・2低では軒高7m超又は3階以上）",
        "sign_period": "",
        "uses_metro_ordinance": True,
        "regulation_url": "https://www.city.akiruno.tokyo.jp/0000000742.html",
        "demolition": {
            "target_area": 80,
            "sign_deadline_wood": 7,
            "sign_deadline_other": 7,
            "requires_submission": False,
            "form_note": "建設リサイクル法に基づく届出のみ（独自の解体事前周知制度なし）",
        },
    },
}


def get_ward_config(ward_name):
    """自治体名（区/市なし）から設定を取得

    Args:
        ward_name: "新宿", "葛飾", "八王子" など（suffix不要）

    Returns:
        dict: 条例設定。未登録の場合はデフォルト値を返す
    """
    config = WARD_CONFIG.get(ward_name, {})

    # デフォルト値をマージ
    result = dict(_DEFAULT)

    if config:
        result.update(config)
    else:
        # 未登録の自治体 → デフォルトの東京都条例を使用
        # ward_nameに「区」「市」を付けて条例名を生成
        if ward_name:
            result["ordinance_name"] = f"{ward_name}区中高層建築物の建築に係る紛争の予防と調整に関する条例"

    return result


# ========== 手続きガイド ==========

def get_procedure_guide(ward_name):
    """区ごとの手続きステップ・必要書類・注意点を返す

    Returns:
        dict with keys:
          steps: list[dict]  — 手続きステップ（順序付き）
          documents: list[str] — 提出・準備が必要な書類
          sign_requirements: dict — 標識（看板）の設置要件
          tips: list[str] — その区固有の注意点
    """
    wc = get_ward_config(ward_name)
    is_ward = ward_name in [
        "千代田", "中央", "港", "新宿", "文京", "台東", "墨田", "江東",
        "品川", "目黒", "大田", "世田谷", "渋谷", "中野", "杉並", "豊島",
        "北", "荒川", "板橋", "練馬", "足立", "葛飾", "江戸川",
    ]
    suffix = "区" if is_ward else "市"

    # --- 手続きステップ ---
    steps = [
        {
            "order": 1,
            "title": "対象確認",
            "detail": f"建築計画が中高層条例の対象か確認（{wc['height_threshold']}）",
        },
        {
            "order": 2,
            "title": "標識（看板）の設置",
            "detail": f"建築計画の概要を記載した標識を現地に設置（根拠: {wc['sign_article']}）",
        },
        {
            "order": 3,
            "title": "標識設置届の提出",
            "detail": f"{ward_name}{suffix}長 宛てに届出"
                      + (f"（期限: {wc['sign_period']}）" if wc.get("sign_period") else ""),
        },
        {
            "order": 4,
            "title": "近隣住民への説明",
            "detail": f"説明範囲内の住民に建築計画を説明（根拠: {wc['explanation_article']}）。個別訪問・説明会・書面配布など",
        },
        {
            "order": 5,
            "title": "近隣説明報告書の提出",
            "detail": f"説明実施後、{ward_name}{suffix}長 宛てに報告書を提出",
        },
        {
            "order": 6,
            "title": "確認申請",
            "detail": "上記手続き完了後、建築確認申請へ進む",
        },
    ]

    # --- 提出・準備書類 ---
    documents = [
        {"name": "標識設置届", "how": "本アプリで生成可能", "required": True},
        {"name": "近隣説明報告書", "how": "本アプリで生成可能", "required": True},
        {"name": "近隣説明範囲図（地図）", "how": "本アプリで生成可能", "required": True},
        {"name": "標識（看板）本体", "how": "現場に設置する実物。サイズ・記載事項は各区の様式を参照", "required": True},
        {"name": "工事のお知らせ", "how": "本アプリで生成可能（近隣配布用）", "required": False},
        {"name": "建築計画概要書", "how": "確認申請書類に含まれる（別途作成）", "required": False},
    ]

    # 区固有の書類
    cfg = WARD_CONFIG.get(ward_name, {})
    if cfg.get("uses_metro_ordinance"):
        if is_ward:
            documents.append({
                "name": "東京都条例に基づく届出書",
                "how": "東京都の様式を使用（区の指導要綱と併用）",
                "required": True,
            })
        else:
            documents.append({
                "name": "東京都条例に基づく届出書",
                "how": "東京都多摩建築指導事務所の様式を使用",
                "required": True,
            })

    # --- 標識（看板）の設置要件 ---
    sign_req = {
        "location": "建築予定地の道路に面する見やすい場所",
        "timing": wc.get("sign_period", "確認申請前（期限は区の窓口で確認）"),
        "content": "建築主名、設計者名、施工者名、建物概要（用途・構造・高さ・階数等）、説明範囲",
        "note": "看板のサイズ・記載事項は各区の条例・要綱で定められています。公式様式を確認してください。",
    }

    # --- 注意点 ---
    tips = []
    if wc.get("note"):
        tips.append(wc["note"])
    if wc.get("uses_metro_ordinance"):
        if is_ward:
            tips.append("この区は独自条例ではなく指導要綱です。東京都条例と併用されます。")
        else:
            tips.append("この市は独自条例を持たず、東京都条例が直接適用されます。届出先は東京都多摩建築指導事務所です。")
    if not tips:
        tips.append(f"詳細は{ward_name}{suffix}の建築課窓口にお問い合わせください。")

    return {
        "steps": steps,
        "documents": documents,
        "sign_requirements": sign_req,
        "tips": tips,
        "regulation_url": wc.get("regulation_url", ""),
    }
