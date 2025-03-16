"""
カスタマーサポートチャットボット用の商品データベース

このモジュールは、商品情報、よくある質問、およびポリシー情報を提供します。
実際のアプリケーションでは、これらのデータはデータベースから取得します。
"""

# 商品カタログ
PRODUCTS = {
    "TS-100": {
        "name": "プレミアムコーヒーメーカー TS-100",
        "price": 12800,
        "description": "高品質なステンレス製のコーヒーメーカー。温度制御機能と豊富なプリセットプログラムを搭載。",
        "specs": {
            "容量": "1.2L",
            "サイズ": "25cm x 18cm x 35cm",
            "重量": "3.5kg",
            "電源": "AC100V, 900W",
            "機能": "温度制御, タイマー, 自動電源オフ",
            "保証期間": "1年",
        },
        "stock_status": "在庫あり",
        "category": "キッチン家電",
    },
    "TS-200": {
        "name": "ハイエンドコーヒーメーカー TS-200",
        "price": 24800,
        "description": "IoT対応の高機能コーヒーメーカー。スマートフォンでの遠隔操作が可能で、豆の挽き具合も調整できる。",
        "specs": {
            "容量": "1.5L",
            "サイズ": "30cm x 22cm x 40cm",
            "重量": "4.2kg",
            "電源": "AC100V, 1200W",
            "機能": "温度制御, タイマー, 自動電源オフ, Wi-Fi接続, 豆挽き機能",
            "保証期間": "2年",
        },
        "stock_status": "在庫あり",
        "category": "キッチン家電",
    },
    "TB-100": {
        "name": "デジタルトースター TB-100",
        "price": 8500,
        "description": "6段階の焼き加減調整が可能なデジタルトースター。広い庫内で食パンが4枚同時に焼ける。",
        "specs": {
            "サイズ": "32cm x 28cm x 22cm",
            "重量": "3.0kg",
            "電源": "AC100V, 1300W",
            "機能": "6段階焼き加減調整, タイマー, 自動電源オフ",
            "保証期間": "1年",
        },
        "stock_status": "在庫あり",
        "category": "キッチン家電",
    },
    "BL-300": {
        "name": "パワーブレンダー BL-300",
        "price": 16800,
        "description": "1000Wの強力モーターを搭載したハイパワーブレンダー。硬い食材も簡単に粉砕できる。",
        "specs": {
            "容量": "1.8L",
            "サイズ": "18cm x 18cm x 42cm",
            "重量": "3.8kg",
            "電源": "AC100V, 1000W",
            "機能": "5段階速度調整, パルス機能, 自動洗浄",
            "保証期間": "1年",
        },
        "stock_status": "残りわずか",
        "category": "キッチン家電",
    },
    "RC-500": {
        "name": "スマート炊飯器 RC-500",
        "price": 32800,
        "description": "AIが火加減を自動調整する次世代の炊飯器。多彩な炊き分けメニューと遠隔操作に対応。",
        "specs": {
            "容量": "5.5合",
            "サイズ": "26cm x 32cm x 24cm",
            "重量": "6.5kg",
            "電源": "AC100V, 1400W",
            "機能": "AIモード, 保温, 予約, Wi-Fi接続",
            "保証期間": "3年",
        },
        "stock_status": "在庫あり",
        "category": "キッチン家電",
    },
}

# よくある質問（FAQ）
FAQS = [
    {
        "question": "商品の保証期間はどのくらいですか？",
        "answer": "商品の保証期間は製品によって異なります。基本的には購入日から1年間の製品保証が付いていますが、一部の高級モデルでは2年または3年の保証期間が設定されています。具体的な保証期間は各商品の詳細ページでご確認いただけます。",
    },
    {
        "question": "返品・交換はできますか？",
        "answer": "はい、商品到着後8日以内であれば、未使用・未開封の状態に限り返品・交換を承っております。返品をご希望の場合は、カスタマーサポートまでご連絡ください。なお、お客様都合による返品の場合は、返送料はお客様のご負担となりますのでご了承ください。",
    },
    {
        "question": "配送にはどれくらいの時間がかかりますか？",
        "answer": "通常、ご注文確定後1-3営業日以内に発送いたします。配送方法は佐川急便または日本郵便を利用しており、発送後1-2日程度でお届けいたします。離島や一部地域では配送に追加の日数がかかる場合があります。",
    },
    {
        "question": "注文のキャンセルはできますか？",
        "answer": "発送前であればキャンセルが可能です。マイページの注文履歴からキャンセル手続きを行うか、カスタマーサポートまでご連絡ください。ただし、すでに発送処理が完了している場合はキャンセルできませんので、商品到着後に返品手続きをお願いいたします。",
    },
    {
        "question": "商品に不具合があった場合はどうすればよいですか？",
        "answer": "商品に不具合がある場合は、すぐにカスタマーサポートまでご連絡ください。保証期間内であれば、無償で修理または交換対応いたします。お問い合わせの際には、購入証明書と不具合の詳細をお知らせいただくとスムーズに対応できます。",
    },
    {
        "question": "支払い方法にはどのようなものがありますか？",
        "answer": "クレジットカード（VISA、Mastercard、JCB、American Express）、PayPay、コンビニ決済、銀行振込に対応しています。クレジットカードとPayPayの場合は即時決済となり、コンビニ決済と銀行振込は入金確認後の発送となります。",
    },
]

# 会社ポリシー
POLICIES = {
    "shipping": {
        "title": "配送ポリシー",
        "content": "当社では、日本全国への配送を承っております。配送料は一律550円（税込）ですが、税込11,000円以上のご注文の場合は送料無料となります。通常、ご注文確定後1-3営業日以内に商品を発送いたします。離島および一部地域では、追加料金または日数がかかる場合がございます。",
    },
    "returns": {
        "title": "返品・交換ポリシー",
        "content": "商品到着後8日以内であれば、未使用・未開封の状態に限り返品・交換を承っております。不良品・誤送品の場合は当社が返送料を負担いたしますが、お客様都合による返品の場合は、返送料はお客様のご負担となります。返品商品が当社に到着し、検品後に返金処理を行います。",
    },
    "warranty": {
        "title": "保証ポリシー",
        "content": "当社の商品は、購入日から一定期間の製品保証が付いています。保証期間内に正常な使用状態で故障した場合は、無償で修理または交換いたします。ただし、お客様の過失による故障・損傷、自然災害による故障、消耗品の交換は保証対象外となります。保証サービスをご利用の際は、購入証明書が必要となります。",
    },
    "privacy": {
        "title": "プライバシーポリシー",
        "content": "当社は、お客様の個人情報を厳重に管理し、適切に取り扱います。収集した個人情報は、注文処理、配送、アフターサービス、マーケティング活動にのみ使用し、お客様の同意なく第三者に提供することはありません。お客様は、自身の個人情報へのアクセス、訂正、削除を要求する権利を有しています。",
    },
}

# 注文状況（模擬データ）
ORDERS = {
    "ORD-12345": {
        "customer_id": "CUST-789",
        "date": "2023-12-10",
        "status": "配送中",
        "tracking_number": "1234-5678-90",
        "items": [
            {"product_id": "TS-100", "quantity": 1, "price": 12800},
            {"product_id": "TB-100", "quantity": 1, "price": 8500},
        ],
        "total": 21300,
        "shipping_address": "東京都新宿区西新宿1-1-1",
        "estimated_delivery": "2023-12-15",
    },
    "ORD-12346": {
        "customer_id": "CUST-456",
        "date": "2023-12-12",
        "status": "準備中",
        "items": [
            {"product_id": "BL-300", "quantity": 1, "price": 16800},
        ],
        "total": 16800,
        "shipping_address": "大阪府大阪市北区梅田1-1-1",
        "estimated_delivery": "2023-12-18",
    },
    "ORD-12347": {
        "customer_id": "CUST-123",
        "date": "2023-12-05",
        "status": "配送済み",
        "tracking_number": "2345-6789-01",
        "items": [
            {"product_id": "RC-500", "quantity": 1, "price": 32800},
        ],
        "total": 32800,
        "shipping_address": "福岡県福岡市博多区博多駅前1-1-1",
        "estimated_delivery": "2023-12-10",
        "delivery_date": "2023-12-09",
    },
}


# ツール関数
def get_product_info(product_id):
    """商品情報を取得します。"""
    if product_id in PRODUCTS:
        return PRODUCTS[product_id]
    return {"error": f"商品 {product_id} が見つかりません"}


def search_products(query, category=None):
    """商品を検索します。"""
    results = []
    for product_id, product in PRODUCTS.items():
        if query.lower() in product["name"].lower() or query.lower() in product["description"].lower():
            if category is None or product["category"] == category:
                results.append({"id": product_id, **product})
    return {"results": results, "count": len(results)}


def get_faq(query=None):
    """FAQを検索します。"""
    if query is None:
        return {"faqs": FAQS}
    
    results = []
    for faq in FAQS:
        if query.lower() in faq["question"].lower() or query.lower() in faq["answer"].lower():
            results.append(faq)
    return {"faqs": results, "count": len(results)}


def get_policy(policy_type):
    """ポリシー情報を取得します。"""
    if policy_type in POLICIES:
        return POLICIES[policy_type]
    return {"error": f"ポリシータイプ {policy_type} が見つかりません"}


def get_order_status(order_id):
    """注文状況を取得します。"""
    if order_id in ORDERS:
        return ORDERS[order_id]
    return {"error": f"注文 {order_id} が見つかりません"}