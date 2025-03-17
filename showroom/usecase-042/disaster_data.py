from pydantic import BaseModel
from typing import List, Dict, Optional, Literal
from datetime import datetime

# 災害種別
DISASTER_TYPES = {
    "earthquake": "地震",
    "flood": "洪水",
    "tsunami": "津波",
    "fire": "火災",
    "typhoon": "台風",
    "landslide": "土砂災害",
    "volcano": "火山噴火",
    "heatwave": "熱波",
    "snowstorm": "大雪",
}

# 警戒レベル
ALERT_LEVELS = {
    "info": "情報",
    "advisory": "注意報",
    "warning": "警報",
    "emergency": "緊急警報",
}

# 対象グループ
TARGET_GROUPS = {
    "general": "一般市民",
    "elderly": "高齢者",
    "children": "子ども・保護者",
    "disabled": "障がい者",
    "foreigners": "外国人",
    "tourists": "観光客",
}

# 言語
LANGUAGES = {
    "ja": "日本語",
    "en": "英語",
    "easy_ja": "やさしい日本語",
}


# 災害情報モデル
class DisasterInfo(BaseModel):
    id: Optional[str] = None
    disaster_type: str
    alert_level: str
    title: str
    description: str
    affected_areas: List[str]
    evacuation_centers: List[Dict[str, str]] = []
    start_time: datetime
    estimated_end_time: Optional[datetime] = None
    instructions: str
    emergency_contacts: Dict[str, str]
    update_time: datetime = datetime.now()

    def get_formatted_affected_areas(self) -> str:
        return "、".join(self.affected_areas)

    def get_formatted_evacuation_centers(self) -> str:
        if not self.evacuation_centers:
            return "なし"
        return "、".join(
            [
                f"{center['name']}（{center['address']}）"
                for center in self.evacuation_centers
            ]
        )


# 災害テンプレート
DISASTER_TEMPLATES = {
    "earthquake": {
        "info": "地震情報をお知らせします。{title}が発生しました。{description}",
        "advisory": "地震注意報が発令されました。{title}　{description}　今後の情報に注意してください。",
        "warning": "⚠️地震警報⚠️ {title}　{description}　{instructions}",
        "emergency": "‼️緊急地震速報‼️ {title}　{description}　直ちに{instructions}",
    },
    "tsunami": {
        "info": "津波情報をお知らせします。{title}　{description}",
        "advisory": "津波注意報が発令されました。{title}　{description}　海岸付近にいる方は注意してください。",
        "warning": "⚠️津波警報⚠️ {title}　{description}　{instructions}",
        "emergency": "‼️大津波警報‼️ {title}　{description}　直ちに高台または避難ビルへ避難してください。{instructions}",
    },
    # 他の災害種別のテンプレートも同様に定義
}

# サンプル災害データ
SAMPLE_DISASTERS = [
    {
        "id": "eq20250317001",
        "disaster_type": "earthquake",
        "alert_level": "warning",
        "title": "東京湾北部地震",
        "description": "3月17日午前10時30分頃、東京湾北部を震源とするマグニチュード5.5の地震が発生しました。東京都内で最大震度5弱を観測しています。",
        "affected_areas": [
            "東京都千代田区",
            "東京都中央区",
            "東京都港区",
            "東京都新宿区",
        ],
        "evacuation_centers": [
            {"name": "千代田区立九段小学校", "address": "千代田区九段南2-1-11"},
            {"name": "港区立芝公園小学校", "address": "港区芝公園3-5-37"},
        ],
        "start_time": "2025-03-17T10:30:00",
        "estimated_end_time": None,
        "instructions": "落ち着いて行動し、テレビやラジオ、防災無線の情報に注意してください。余震に備えてください。",
        "emergency_contacts": {
            "police": "110",
            "fire": "119",
            "disaster_info": "03-1234-5678",
        },
        "update_time": "2025-03-17T10:45:00",
    },
    {
        "id": "ty20250315001",
        "disaster_type": "typhoon",
        "alert_level": "warning",
        "title": "台風8号接近",
        "description": "大型で非常に強い台風8号が本州に接近しています。最大風速45m/s、瞬間最大風速60m/sの見込みです。",
        "affected_areas": ["東京都全域", "神奈川県全域", "千葉県全域", "埼玉県南部"],
        "evacuation_centers": [
            {
                "name": "各市区町村の指定避難所",
                "address": "お住まいの自治体にお問い合わせください",
            }
        ],
        "start_time": "2025-03-18T00:00:00",
        "estimated_end_time": "2025-03-19T12:00:00",
        "instructions": "不要不急の外出を控え、早めに安全な場所に避難してください。停電に備えて懐中電灯や携帯ラジオ、モバイルバッテリーを準備してください。",
        "emergency_contacts": {
            "weather_info": "177",
            "disaster_prevention": "03-9876-5432",
        },
        "update_time": "2025-03-17T16:00:00",
    },
]


def load_sample_disasters() -> List[DisasterInfo]:
    """サンプル災害データをDisasterInfoオブジェクトのリストとして返す"""
    return [DisasterInfo(**disaster) for disaster in SAMPLE_DISASTERS]
