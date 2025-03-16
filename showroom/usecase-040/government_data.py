"""
市民向け行政サービス案内のデータモジュール

このモジュールは、行政手続き情報、施設情報、イベント情報、FAQ、緊急情報などの
データを管理し、検索・取得するための関数を提供します。
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any


# --- サンプルデータ ---

# 行政手続き情報
PROCEDURES = [
    {
        "id": "CERT-001",
        "name": "住民票の写し",
        "category": "residence",
        "description": "住民登録されている住所や世帯構成などを証明する書類です。",
        "required_documents": ["本人確認書類（運転免許証、マイナンバーカードなど）"],
        "fee": 300,
        "processing_time": "即日（窓口申請の場合）",
        "online_available": True,
        "locations": ["市役所本庁舎1階市民課", "各地域センター"],
        "hours": "平日 8:30～17:15（土日祝日、年末年始を除く）",
        "notes": "同一世帯以外の方が申請する場合は委任状が必要です。"
    },
    {
        "id": "CERT-002",
        "name": "印鑑登録証明書",
        "category": "residence",
        "description": "登録された印鑑の印影を証明する書類です。",
        "required_documents": ["印鑑登録証（カード）", "本人確認書類"],
        "fee": 300,
        "processing_time": "即日（窓口申請の場合）",
        "online_available": True,
        "locations": ["市役所本庁舎1階市民課", "各地域センター"],
        "hours": "平日 8:30～17:15（土日祝日、年末年始を除く）",
        "notes": "印鑑登録証（カード）が必要です。紛失した場合は再登録が必要となります。"
    },
    {
        "id": "TAX-001",
        "name": "所得課税証明書",
        "category": "tax",
        "description": "所得金額や課税額を証明する書類です。",
        "required_documents": ["本人確認書類（運転免許証、マイナンバーカードなど）"],
        "fee": 300,
        "processing_time": "即日（窓口申請の場合）",
        "online_available": True,
        "locations": ["市役所本庁舎2階税務課", "各地域センター"],
        "hours": "平日 8:30～17:15（土日祝日、年末年始を除く）",
        "notes": "最新年度分の証明書は6月中旬頃から発行可能となります。"
    },
    {
        "id": "TAX-002",
        "name": "固定資産税納税証明書",
        "category": "tax",
        "description": "固定資産税の納付状況を証明する書類です。",
        "required_documents": ["本人確認書類（運転免許証、マイナンバーカードなど）"],
        "fee": 300,
        "processing_time": "即日（窓口申請の場合）",
        "online_available": True,
        "locations": ["市役所本庁舎2階税務課"],
        "hours": "平日 8:30～17:15（土日祝日、年末年始を除く）",
        "notes": "納税義務者以外の方が申請する場合は委任状が必要です。"
    },
    {
        "id": "WEL-001",
        "name": "児童手当申請",
        "category": "welfare",
        "description": "中学校卒業までの児童を養育している方への手当申請手続きです。",
        "required_documents": [
            "本人確認書類",
            "請求者名義の預金通帳またはキャッシュカード",
            "健康保険証の写し",
            "（公務員の場合）勤務先からの証明書"
        ],
        "fee": 0,
        "processing_time": "申請月の翌月から支給開始",
        "online_available": False,
        "locations": ["市役所本庁舎3階子育て支援課", "各地域センター"],
        "hours": "平日 8:30～17:15（土日祝日、年末年始を除く）",
        "notes": "出生や転入の場合は、15日以内に申請が必要です。"
    },
    {
        "id": "WEL-002",
        "name": "介護保険要介護認定申請",
        "category": "welfare",
        "description": "介護サービスを利用するために必要な要介護認定の申請手続きです。",
        "required_documents": [
            "介護保険被保険者証",
            "本人確認書類",
            "医療保険被保険者証（第2号被保険者の場合）"
        ],
        "fee": 0,
        "processing_time": "申請から30日程度",
        "online_available": False,
        "locations": ["市役所本庁舎3階高齢福祉課", "各地域包括支援センター"],
        "hours": "平日 8:30～17:15（土日祝日、年末年始を除く）",
        "notes": "申請後、訪問調査と主治医意見書に基づき審査されます。"
    }
]

# 施設情報
FACILITIES = [
    {
        "id": "LIB-001",
        "name": "中央図書館",
        "facility_type": "library",
        "address": "〒123-4567 市中央区本町1-1-1",
        "phone": "012-345-6789",
        "hours": "火～金：10:00～19:00、土日祝：10:00～17:00",
        "closed_days": "毎週月曜日（祝日の場合は翌平日）、年末年始、特別整理期間",
        "services": [
            "図書・雑誌の貸出・閲覧",
            "視聴覚資料の貸出・視聴",
            "レファレンスサービス",
            "複写サービス",
            "インターネット閲覧",
            "おはなし会"
        ],
        "facilities": ["学習室", "会議室", "視聴覚ブース", "児童コーナー"],
        "website": "https://www.city.example.lg.jp/library/",
        "notes": "駐車場は30台分あります。混雑時は公共交通機関をご利用ください。"
    },
    {
        "id": "LIB-002",
        "name": "北部図書館",
        "facility_type": "library",
        "address": "〒123-4568 市北区北町2-2-2",
        "phone": "012-345-6790",
        "hours": "火～金：10:00～19:00、土日祝：10:00～17:00",
        "closed_days": "毎週月曜日（祝日の場合は翌平日）、年末年始、特別整理期間",
        "services": [
            "図書・雑誌の貸出・閲覧",
            "レファレンスサービス",
            "複写サービス",
            "インターネット閲覧",
            "おはなし会"
        ],
        "facilities": ["学習室", "児童コーナー"],
        "website": "https://www.city.example.lg.jp/library/north/",
        "notes": "駐車場は15台分あります。"
    },
    {
        "id": "COMM-001",
        "name": "中央公民館",
        "facility_type": "community",
        "address": "〒123-4567 市中央区本町2-3-4",
        "phone": "012-345-6791",
        "hours": "9:00～21:00",
        "closed_days": "毎月第3月曜日（祝日の場合は翌平日）、年末年始",
        "services": [
            "各種講座・教室の開催",
            "会議室・ホールの貸出",
            "サークル活動支援",
            "生涯学習相談"
        ],
        "facilities": ["多目的ホール（200人）", "会議室（30人×3室）", "調理実習室", "和室", "工作室"],
        "website": "https://www.city.example.lg.jp/community/central/",
        "notes": "施設の予約は使用日の2か月前から可能です。団体登録が必要です。"
    },
    {
        "id": "SPORT-001",
        "name": "市民総合体育館",
        "facility_type": "sports",
        "address": "〒123-4570 市南区スポーツ町1-1-1",
        "phone": "012-345-6793",
        "hours": "9:00～21:00",
        "closed_days": "毎月第2月曜日（祝日の場合は翌平日）、年末年始",
        "services": [
            "各種スポーツ教室の開催",
            "施設の貸出",
            "スポーツ用具の貸出",
            "トレーニング指導"
        ],
        "facilities": [
            "メインアリーナ",
            "サブアリーナ",
            "トレーニングルーム",
            "プール",
            "武道場",
            "会議室"
        ],
        "website": "https://www.city.example.lg.jp/sports/gym/",
        "notes": "トレーニングルームは中学生以上から利用可能です。利用者講習会の受講が必要です。"
    },
    {
        "id": "GOV-001",
        "name": "市役所本庁舎",
        "facility_type": "government",
        "address": "〒123-4567 市中央区本町1-1",
        "phone": "012-345-6700",
        "hours": "平日 8:30～17:15",
        "closed_days": "土日祝日、年末年始（12月29日～1月3日）",
        "services": [
            "各種証明書発行",
            "届出・申請手続き",
            "相談業務",
            "税金の納付"
        ],
        "facilities": ["市民課", "税務課", "福祉課", "子育て支援課", "高齢福祉課", "保険年金課", "都市計画課", "環境課"],
        "website": "https://www.city.example.lg.jp/",
        "notes": "毎週木曜日は一部窓口（市民課・税務課）を19:00まで延長しています。"
    },
    {
        "id": "CULT-001",
        "name": "市民文化会館",
        "facility_type": "culture",
        "address": "〒123-4571 市中央区文化町3-3-3",
        "phone": "012-345-6794",
        "hours": "9:00～21:00",
        "closed_days": "毎月第4月曜日（祝日の場合は翌平日）、年末年始",
        "services": [
            "コンサート・演劇等の公演",
            "施設の貸出",
            "文化芸術講座の開催"
        ],
        "facilities": [
            "大ホール（1000席）",
            "小ホール（300席）",
            "展示室",
            "練習室（音楽・舞踊）",
            "会議室"
        ],
        "website": "https://www.city.example.lg.jp/culture/hall/",
        "notes": "施設の予約は利用日の6か月前から可能です。専用の予約システムからお申込みください。"
    }
]

# イベント情報
# 現在の日付を基準にイベントデータを生成
TODAY = datetime.now()
EVENTS = [
    {
        "id": "EVENT-001",
        "name": "市民健康フェスティバル",
        "event_type": "festival",
        "date": (TODAY + timedelta(days=15)).strftime("%Y-%m-%d"),
        "time": "10:00～16:00",
        "location": "市民総合体育館",
        "description": "健康チェック、運動指導、栄養相談など、市民の健康増進を目的としたイベントです。",
        "target": "市民全般",
        "fee": "無料",
        "capacity": "定員なし",
        "registration": "不要",
        "contact": "健康推進課（012-345-6780）",
        "notes": "動きやすい服装でお越しください。一部コーナーでは整理券を配布します。"
    },
    {
        "id": "EVENT-002",
        "name": "子育て支援セミナー",
        "event_type": "seminar",
        "date": (TODAY + timedelta(days=7)).strftime("%Y-%m-%d"),
        "time": "13:30～15:30",
        "location": "中央公民館 多目的ホール",
        "description": "子育ての悩みや不安を軽減するためのセミナーです。専門家による講演と質疑応答が行われます。",
        "target": "就学前の子どもを持つ保護者",
        "fee": "無料",
        "capacity": "100名（先着順）",
        "registration": "要（電話または市公式ウェブサイトから）",
        "contact": "子育て支援課（012-345-6781）",
        "notes": "託児サービスあり（要予約、1歳以上、定員20名）"
    },
    {
        "id": "EVENT-003",
        "name": "確定申告相談会",
        "event_type": "consultation",
        "date": (TODAY + timedelta(days=10)).strftime("%Y-%m-%d"),
        "time": "9:00～16:00",
        "location": "市役所本庁舎2階 税務課",
        "description": "市民税・県民税の申告および所得税の確定申告の相談・受付を行います。",
        "target": "申告が必要な市民",
        "fee": "無料",
        "capacity": "1日50名程度（先着順）",
        "registration": "不要（受付順）",
        "contact": "税務課（012-345-6782）",
        "notes": "申告に必要な書類（源泉徴収票、医療費の領収書、控除証明書など）を持参してください。"
    },
    {
        "id": "EVENT-004",
        "name": "市民音楽祭",
        "event_type": "festival",
        "date": (TODAY + timedelta(days=21)).strftime("%Y-%m-%d"),
        "time": "13:00～17:00",
        "location": "市民文化会館 大ホール",
        "description": "市内の音楽団体や学校による演奏会です。クラシックから現代音楽まで幅広いジャンルの音楽をお楽しみいただけます。",
        "target": "市民全般",
        "fee": "無料（要整理券）",
        "capacity": "1000名",
        "registration": "整理券は文化会館、各地域センター、市役所で配布",
        "contact": "文化振興課（012-345-6783）",
        "notes": "未就学児の入場はご遠慮ください。"
    },
    {
        "id": "EVENT-005",
        "name": "防災ワークショップ",
        "event_type": "workshop",
        "date": (TODAY + timedelta(days=14)).strftime("%Y-%m-%d"),
        "time": "10:00～12:00",
        "location": "防災センター",
        "description": "災害時の対応や備えについて学ぶワークショップです。避難所運営ゲームや非常食の試食なども行います。",
        "target": "市民全般",
        "fee": "無料",
        "capacity": "30名（先着順）",
        "registration": "要（電話または市公式ウェブサイトから）",
        "contact": "防災課（012-345-6784）",
        "notes": "小学生以下のお子様は保護者同伴でご参加ください。"
    },
    {
        "id": "EVENT-006",
        "name": "シニア向けスマホ教室",
        "event_type": "workshop",
        "date": (TODAY + timedelta(days=5)).strftime("%Y-%m-%d"),
        "time": "14:00～16:00",
        "location": "中央公民館 会議室1",
        "description": "スマートフォンの基本操作から、便利なアプリの使い方まで丁寧に説明します。初心者向けの内容です。",
        "target": "60歳以上の市民",
        "fee": "無料",
        "capacity": "20名（先着順）",
        "registration": "要（電話または各公民館窓口で受付）",
        "contact": "生涯学習課（012-345-6785）",
        "notes": "スマートフォンをお持ちの方はご持参ください。お持ちでない方も参加できます。"
    }
]

# FAQ情報
FAQS = [
    {
        "id": "FAQ-001",
        "category": "garbage",
        "question": "ゴミの出し方や分別方法について知りたいです。",
        "answer": "ゴミは以下のように分別してください：\n1. 燃やせるゴミ：毎週月・木曜日に収集\n2. 燃やせないゴミ：毎月第2・4水曜日に収集\n3. 資源ゴミ（缶・びん・ペットボトル）：毎週火曜日に収集\n4. 資源ゴミ（紙類・古布）：毎月第1・3水曜日に収集\n5. 粗大ゴミ：事前申込制（環境課へ電話または市公式ウェブサイトから申込）\n\n詳しくは「市民ゴミ分別ガイドブック」をご覧いただくか、環境課（012-345-6760）までお問い合わせください。"
    },
    {
        "id": "FAQ-002",
        "category": "garbage",
        "question": "引っ越しや大掃除で出た大量のゴミはどうすればいいですか？",
        "answer": "引っ越しや大掃除で一時的に大量のゴミが出る場合は、以下の方法があります：\n\n1. 分別して通常の収集日に少しずつ出す\n2. 粗大ゴミ収集を利用する（事前申込制、有料）\n3. クリーンセンターに直接持ち込む（要事前連絡、有料）\n\n特に多量の場合は環境課（012-345-6760）にご相談ください。民間の廃棄物処理業者をご紹介することもできます。"
    },
    {
        "id": "FAQ-003",
        "category": "tax",
        "question": "市民税・県民税の納付方法を教えてください。",
        "answer": "市民税・県民税は以下の方法で納付できます：\n\n1. 納付書による支払い：金融機関、コンビニエンスストア、市役所・各地域センターの窓口\n2. 口座振替：お申し込みは金融機関の窓口で「口座振替依頼書」に必要事項を記入・押印\n3. スマートフォン決済アプリ：PayPay、LINE Pay等（納付書のバーコードを読み取り）\n4. クレジットカード納付：市公式ウェブサイトの「税金の電子納付」ページから（手数料がかかります）\n\n納付に関するご質問は税務課収納係（012-345-6762）までお問い合わせください。"
    },
    {
        "id": "FAQ-004",
        "category": "tax",
        "question": "固定資産税はいつ頃、どのように納付するのですか？",
        "answer": "固定資産税の納付時期と方法は以下の通りです：\n\n【納付時期】\n第1期：4月末日\n第2期：7月末日\n第3期：12月末日\n第4期：翌年2月末日\n※一括納付も可能です。\n\n【納付方法】\n1. 納付書による支払い：金融機関、コンビニエンスストア、市役所・各地域センターの窓口\n2. 口座振替：お申し込みは金融機関の窓口で「口座振替依頼書」に必要事項を記入・押印\n3. スマートフォン決済アプリ：PayPay、LINE Pay等（納付書のバーコードを読み取り）\n4. クレジットカード納付：市公式ウェブサイトの「税金の電子納付」ページから（手数料がかかります）\n\n納税通知書は毎年5月上旬に発送されます。届かない場合や紛失した場合は税務課資産税係（012-345-6763）までご連絡ください。"
    },
    {
        "id": "FAQ-005",
        "category": "childcare",
        "question": "保育園の入園申し込み方法と時期について教えてください。",
        "answer": "保育園の入園申し込みについては以下の通りです：\n\n【申込時期】\n・次年度4月からの入園：例年10月上旬から11月中旬まで\n・年度途中の入園：希望する月の前月10日まで（例：6月入園希望の場合は5月10日まで）\n\n【申込方法】\n1. 市公式ウェブサイトから「保育所等利用申込書」などの必要書類をダウンロード\n2. 必要事項を記入し、必要書類を添えて子育て支援課または各地域センターに提出\n\n【必要書類】\n・保育所等利用申込書\n・保育の必要性を証明する書類（就労証明書、診断書など）\n・世帯状況・税情報等に関する同意書\n・その他状況に応じて必要な書類\n\n詳しくは子育て支援課保育係（012-345-6765）までお問い合わせください。"
    },
    {
        "id": "FAQ-006",
        "category": "childcare",
        "question": "子育て支援センターはどのような施設ですか？利用方法を教えてください。",
        "answer": "子育て支援センターは、乳幼児とその保護者が自由に利用できる施設です。以下の活動を行っています：\n\n【主な活動内容】\n・親子で自由に遊べるスペースの提供\n・育児相談の実施\n・親子向けのイベントや講座の開催\n・子育てサークルの支援\n・子育て情報の提供\n\n【利用方法】\n・開館時間：月～金曜日 9:00～16:00（祝日、年末年始を除く）\n・利用料：無料\n・予約：不要（イベントや講座は事前申込が必要な場合あり）\n・対象：0歳～就学前の子どもとその保護者\n\n市内には中央・東部・西部・南部・北部の5か所に子育て支援センターがあります。最寄りの支援センターについては子育て支援課（012-345-6765）にお問い合わせください。"
    },
    {
        "id": "FAQ-007",
        "category": "elderly",
        "question": "高齢者向けの福祉サービスにはどのようなものがありますか？",
        "answer": "本市では高齢者の方が安心して暮らせるよう、以下のようなサービスを提供しています：\n\n1. 介護保険サービス：\n   - 訪問介護、通所介護、短期入所生活介護など\n   - 要介護・要支援認定が必要です\n\n2. 介護予防サービス：\n   - 介護予防教室、健康体操教室、認知症予防講座など\n   - 65歳以上の方なら誰でも参加できます\n\n3. 日常生活支援サービス：\n   - 配食サービス、外出支援サービス、緊急通報システムなど\n   - 対象要件があるものもあります\n\n4. 相談支援：\n   - 地域包括支援センターでの総合相談\n   - 認知症初期集中支援チームによる支援\n\n詳しくは、高齢福祉課（012-345-6770）または最寄りの地域包括支援センターにお問い合わせください。"
    },
    {
        "id": "FAQ-008",
        "category": "elderly",
        "question": "介護保険の申請はどのようにすればよいですか？",
        "answer": "介護保険サービスを利用するための申請方法は以下の通りです：\n\n【申請方法】\n1. 申請窓口：市役所高齢福祉課、各地域センター、または地域包括支援センター\n2. 必要書類：介護保険被保険者証、本人確認書類（マイナンバーカード、運転免許証など）\n3. 申請者：本人または家族、地域包括支援センター職員、居宅介護支援事業者など\n\n【申請後の流れ】\n1. 認定調査員による訪問調査（約1時間）\n2. 主治医の意見書作成依頼（市から直接主治医に依頼）\n3. 介護認定審査会による審査・判定\n4. 認定結果の通知（申請から30日以内に郵送）\n   - 要支援1・2、要介護1～5のいずれかに認定\n5. ケアプランの作成と介護サービスの利用開始\n\n詳しくは高齢福祉課介護保険係（012-345-6771）または地域包括支援センター（012-345-6772）にお問い合わせください。"
    },
    {
        "id": "FAQ-009",
        "category": "disaster",
        "question": "災害時の避難場所はどこですか？",
        "answer": "災害時の避難場所は災害の種類によって異なります。主な避難場所は以下の通りです：\n\n【指定緊急避難場所】災害の危険から命を守るための一時的な避難場所\n- 洪水・土砂災害：市民総合体育館、中央公民館、各地域センター\n- 地震：各小中学校校庭、市民公園、総合運動公園\n- 大規模火災：総合運動公園、中央公園、河川敷広場\n\n【指定避難所】災害により自宅に戻れない場合などに滞在する施設\n- 各小中学校体育館、市民総合体育館、中央公民館、各地域センターなど\n\n【福祉避難所】特別な配慮が必要な方のための避難所\n- 総合福祉センター、市内福祉施設（協定締結施設）\n\n最寄りの避難場所は「防災マップ」（全戸配布済み）でご確認いただくか、市公式ウェブサイトの「防災情報」ページでご確認ください。スマートフォンアプリ「〇〇市防災アプリ」でも確認できます。\n\n不明な点は防災課（012-345-6775）までお問い合わせください。"
    },
    {
        "id": "FAQ-010",
        "category": "disaster",
        "question": "防災アプリはどのように利用できますか？",
        "answer": "「〇〇市防災アプリ」の主な機能と利用方法は以下の通りです：\n\n【主な機能】\n1. 災害情報のプッシュ通知：避難情報や気象警報など最新情報をお知らせ\n2. 避難所マップ：現在地から最寄りの避難所を表示\n3. ハザードマップ：洪水・土砂災害・地震の危険区域を確認\n4. 防災メモ：家族の集合場所や連絡先などを記録\n5. 災害時チェックリスト：避難時の持ち物や行動確認に活用\n\n【利用方法】\n1. App Store（iPhone）またはGoogle Play（Android）で「〇〇市防災アプリ」を検索\n2. アプリをインストール（無料）\n3. 初回起動時に地域設定（町名）と通知設定を行う\n4. 必要に応じて家族情報などを登録\n\n防災アプリに関するご質問は防災課（012-345-6775）までお問い合わせください。"
    }
]

# 緊急情報
EMERGENCY_INFO = {
    "disaster": {
        "title": "災害情報",
        "info": "現在、市内に発令されている災害情報はありません。",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "details": []
    },
    "weather": {
        "title": "気象情報",
        "info": "明日は晴れの予報です。特別な警報・注意報は発令されていません。",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "details": [
            {
                "type": "予報",
                "content": "明日の天気は晴れ、最高気温28度、最低気温18度の予報です。"
            }
        ]
    },
    "health": {
        "title": "健康・感染症情報",
        "info": "季節性インフルエンザが流行しています。手洗い・うがいを徹底し、体調不良時はマスクの着用をお願いします。",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "details": [
            {
                "type": "インフルエンザ情報",
                "content": "先週の市内医療機関からの報告によると、インフルエンザの患者数が警報レベルに達しています。特に小学校での集団感染が報告されています。"
            },
            {
                "type": "予防接種",
                "content": "インフルエンザの予防接種は市内指定医療機関で受けられます。65歳以上の方は接種費用の一部を市が助成します。"
            }
        ]
    }
}


# --- 検索・取得関数 ---

def get_procedure_info(procedure_id: str) -> Dict:
    """
    手続きIDを指定して手続きの詳細情報を取得します。
    
    Args:
        procedure_id (str): 手続きID（例: CERT-001）
        
    Returns:
        Dict: 手続き情報の辞書
    """
    for procedure in PROCEDURES:
        if procedure["id"] == procedure_id:
            return procedure
    return {"error": "指定された手続きIDが見つかりませんでした。"}


def search_procedures(query: str, category: Optional[str] = None) -> List[Dict]:
    """
    キーワードと任意のカテゴリで行政手続きを検索します。
    
    Args:
        query (str): 検索キーワード
        category (Optional[str]): 手続きカテゴリ（residence:住民関連, tax:税金関連, welfare:福祉関連）
        
    Returns:
        List[Dict]: 検索結果のリスト
    """
    results = []
    
    for procedure in PROCEDURES:
        # キーワード検索（名前と説明文に対して）
        if query.lower() in procedure["name"].lower() or query.lower() in procedure["description"].lower():
            # カテゴリが指定されている場合は、カテゴリも一致するかチェック
            if category is None or procedure["category"] == category:
                results.append(procedure)
    
    return results if results else {"message": "検索条件に一致する手続きが見つかりませんでした。"}


def get_facility_info(facility_id: str) -> Dict:
    """
    施設IDを指定して施設の詳細情報を取得します。
    
    Args:
        facility_id (str): 施設ID（例: LIB-001）
        
    Returns:
        Dict: 施設情報の辞書
    """
    for facility in FACILITIES:
        if facility["id"] == facility_id:
            return facility
    return {"error": "指定された施設IDが見つかりませんでした。"}


def search_facilities(query: str, facility_type: Optional[str] = None) -> List[Dict]:
    """
    キーワードと任意の施設タイプで施設を検索します。
    
    Args:
        query (str): 検索キーワード
        facility_type (Optional[str]): 施設タイプ（library:図書館, community:公民館, sports:スポーツ施設, government:行政施設）
        
    Returns:
        List[Dict]: 検索結果のリスト
    """
    results = []
    
    for facility in FACILITIES:
        # キーワード検索（名前、住所、サービスに対して）
        if (query.lower() in facility["name"].lower() or 
            query.lower() in facility["address"].lower() or 
            any(query.lower() in service.lower() for service in facility["services"])):
            
            # 施設タイプが指定されている場合は、タイプも一致するかチェック
            if facility_type is None or facility["facility_type"] == facility_type:
                results.append(facility)
    
    return results if results else {"message": "検索条件に一致する施設が見つかりませんでした。"}


def get_event_info(event_id: str) -> Dict:
    """
    イベントIDを指定してイベントの詳細情報を取得します。
    
    Args:
        event_id (str): イベントID（例: EVENT-001）
        
    Returns:
        Dict: イベント情報の辞書
    """
    for event in EVENTS:
        if event["id"] == event_id:
            return event
    return {"error": "指定されたイベントIDが見つかりませんでした。"}


def search_events(query: Optional[str] = None, date_from: Optional[str] = None, 
                 date_to: Optional[str] = None, event_type: Optional[str] = None) -> List[Dict]:
    """
    条件を指定してイベントを検索します。
    
    Args:
        query (Optional[str]): 検索キーワード
        date_from (Optional[str]): 開始日（YYYY-MM-DD形式）
        date_to (Optional[str]): 終了日（YYYY-MM-DD形式）
        event_type (Optional[str]): イベントタイプ（seminar:セミナー, festival:お祭り, consultation:相談会, workshop:ワークショップ）
        
    Returns:
        List[Dict]: 検索結果のリスト
    """
    results = []
    
    # 日付範囲の変換
    date_from_obj = datetime.strptime(date_from, "%Y-%m-%d") if date_from else None
    date_to_obj = datetime.strptime(date_to, "%Y-%m-%d") if date_to else None
    
    for event in EVENTS:
        event_date = datetime.strptime(event["date"], "%Y-%m-%d")
        is_match = True
        
        # キーワード検索
        if query and not (query.lower() in event["name"].lower() or query.lower() in event["description"].lower()):
            is_match = False
            
        # 日付範囲の検証
        if date_from_obj and event_date < date_from_obj:
            is_match = False
        if date_to_obj and event_date > date_to_obj:
            is_match = False
            
        # イベントタイプの検証
        if event_type and event["event_type"] != event_type:
            is_match = False
            
        if is_match:
            results.append(event)
    
    return results if results else {"message": "検索条件に一致するイベントが見つかりませんでした。"}


def get_faq(query: Optional[str] = None, category: Optional[str] = None) -> List[Dict]:
    """
    よくある質問（FAQ）を検索します。
    
    Args:
        query (Optional[str]): 検索キーワード
        category (Optional[str]): カテゴリ（garbage:ゴミ, tax:税金, childcare:子育て, elderly:高齢者, disaster:防災）
        
    Returns:
        List[Dict]: 検索結果のリスト
    """
    results = []
    
    for faq in FAQS:
        is_match = True
        
        # キーワード検索
        if query and not (query.lower() in faq["question"].lower() or query.lower() in faq["answer"].lower()):
            is_match = False
            
        # カテゴリの検証
        if category and faq["category"] != category:
            is_match = False
            
        if is_match:
            results.append(faq)
    
    return results if results else {"message": "検索条件に一致するFAQが見つかりませんでした。"}


def get_emergency_info(info_type: Optional[str] = None) -> Dict:
    """
    現在の緊急情報を取得します。
    
    Args:
        info_type (Optional[str]): 情報タイプ（disaster:災害情報, weather:気象情報, health:健康・感染症情報）
        
    Returns:
        Dict: 緊急情報の辞書
    """
    if info_type and info_type in EMERGENCY_INFO:
        return EMERGENCY_INFO[info_type]
    
    # 情報タイプが指定されていない場合や存在しない場合は全情報を返す
    return {
        "all_emergency_info": EMERGENCY_INFO,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }