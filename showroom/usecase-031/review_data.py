"""
製品レビューのサンプルデータ

このモジュールでは、製品レビュー分析のためのサンプルデータを提供します。
実際のアプリケーションでは、これらのデータはデータベースやCSVファイルから読み込みます。
"""

# スマートフォン製品のレビューサンプル
SMARTPHONE_REVIEWS = [
    {
        "product_id": "SP-100",
        "product_name": "TechX Phone Pro",
        "review_id": "R001",
        "customer_id": "C1001",
        "rating": 5,
        "date": "2023-08-15",
        "title": "最高のスマートフォン！",
        "text": "このスマートフォンは今まで使った中で最高です。バッテリーの持ちが非常に良く、1日中使っても余裕があります。カメラの性能も素晴らしく、夜景モードでの撮影が特に気に入っています。処理速度も速く、どんなアプリも問題なく動作します。",
        "helpful_votes": 45,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "SP-100",
        "product_name": "TechX Phone Pro",
        "review_id": "R002",
        "customer_id": "C1002",
        "rating": 4,
        "date": "2023-07-28",
        "title": "ほぼ満足",
        "text": "全体的に満足しています。特にディスプレイの美しさは素晴らしいです。ただ、バッテリーの持ちがカタログスペックほど良くないのが少し残念。それでも以前のスマホよりは格段に良くなりました。指紋認証の反応が時々遅いことがありますが、ソフトウェアアップデートで改善されるとよいと思います。",
        "helpful_votes": 20,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "SP-100",
        "product_name": "TechX Phone Pro",
        "review_id": "R003",
        "customer_id": "C1003",
        "rating": 2,
        "date": "2023-09-05",
        "title": "充電の問題あり",
        "text": "購入後2週間で充電ポートに問題が発生しました。充電ケーブルを挿すときに何度も試さないと認識しません。サポートに連絡しましたが、まだ返答待ちです。画面やカメラは良いのですが、基本的な機能に問題があるとストレスがたまります。",
        "helpful_votes": 32,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "SP-100",
        "product_name": "TechX Phone Pro",
        "review_id": "R004",
        "customer_id": "C1004",
        "rating": 5,
        "date": "2023-09-10",
        "title": "カメラ性能が最高",
        "text": "写真撮影が趣味なので、カメラ性能で選びましたが大正解でした。特に望遠レンズの性能が素晴らしく、遠くの被写体もクリアに撮影できます。ポートレートモードの背景ぼかしも自然で、まるで一眼レフで撮ったような仕上がりになります。UIも直感的で使いやすいです。",
        "helpful_votes": 28,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "SP-100",
        "product_name": "TechX Phone Pro",
        "review_id": "R005",
        "customer_id": "C1005",
        "rating": 3,
        "date": "2023-08-22",
        "title": "普通のスマホ",
        "text": "特に問題はありませんが、この価格帯に対して特別優れているとは思いません。バッテリーは普通、カメラも普通、処理速度も普通です。防水機能は信頼できますが、同じ価格帯の他のメーカーと比べて突出した点が見当たりません。もう少し価格が安ければ評価は高かったと思います。",
        "helpful_votes": 15,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "SP-100",
        "product_name": "TechX Phone Pro",
        "review_id": "R006",
        "customer_id": "C1006",
        "rating": 1,
        "date": "2023-07-15",
        "title": "すぐに故障しました",
        "text": "購入後1ヶ月で突然電源が入らなくなりました。サポートセンターに問い合わせたところ、修理に2週間かかると言われました。これほど高価な製品なのに品質管理が不十分だと感じます。二度と同じメーカーの製品は買いません。",
        "helpful_votes": 42,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "SP-100",
        "product_name": "TechX Phone Pro",
        "review_id": "R007",
        "customer_id": "C1007",
        "rating": 4,
        "date": "2023-09-18",
        "title": "コスパが良い",
        "text": "フラッグシップモデルと比較すると少し性能は劣りますが、この価格帯ではかなり良いと思います。日常使用では全く問題なく、むしろバッテリー持ちの良さは上位モデルよりも優れています。画面の発色も美しく、動画視聴がとても楽しめます。唯一の不満点は、スピーカーの音質がもう少し良ければということです。",
        "helpful_votes": 19,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "SP-100",
        "product_name": "TechX Phone Pro",
        "review_id": "R008",
        "customer_id": "C1008",
        "rating": 5,
        "date": "2023-08-30",
        "title": "期待以上の満足感",
        "text": "正直なところ、あまり期待せずに購入しましたが、使ってみると非常に満足しています。特にOSのカスタマイズ性が高く、自分好みの使い方ができるのが気に入っています。また、セキュリティアップデートが定期的に配信されるので、安心して使えます。防水・防塵性能も信頼できるレベルです。",
        "helpful_votes": 23,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "SP-100",
        "product_name": "TechX Phone Pro",
        "review_id": "R009",
        "customer_id": "C1009",
        "rating": 2,
        "date": "2023-09-25",
        "title": "過熱問題に悩まされています",
        "text": "ゲームをプレイしたり、動画を長時間視聴していると、端末がかなり熱くなります。これが原因でバッテリーの消費も早く、外出時には常に充電器を持ち歩く必要があります。また、熱くなると処理速度も低下するので、ストレスを感じることがあります。夏場の使用は特に厳しいでしょう。",
        "helpful_votes": 30,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "SP-100",
        "product_name": "TechX Phone Pro",
        "review_id": "R010",
        "customer_id": "C1010",
        "rating": 4,
        "date": "2023-10-05",
        "title": "ビジネス用途に最適",
        "text": "仕事で使用していますが、メール管理やスケジュール管理、ドキュメント編集など、ビジネス用途に非常に適しています。バッテリーも一日中持つので安心です。画面分割機能を使えば、複数のアプリを同時に操作できるので効率的です。また、セキュリティ機能も充実しているので、業務データの保護も万全です。",
        "helpful_votes": 17,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "SP-100",
        "product_name": "TechX Phone Pro",
        "review_id": "R011",
        "customer_id": "C1011",
        "rating": 3,
        "date": "2023-08-05",
        "title": "カメラは良いがその他は普通",
        "text": "カメラ性能は確かに優れていますが、それ以外の機能は他の同価格帯のスマートフォンと大差ありません。特に動作の安定性については、時々アプリが突然終了することがあり、もう少し改善の余地があると感じます。また、付属の充電器の充電速度が遅いので、別途急速充電器を購入する必要がありました。",
        "helpful_votes": 12,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "SP-100",
        "product_name": "TechX Phone Pro",
        "review_id": "R012",
        "customer_id": "C1012",
        "rating": 5,
        "date": "2023-09-20",
        "title": "親の操作も簡単",
        "text": "高齢の親にプレゼントしましたが、とても使いやすいようで喜んでいます。UIがシンプルで直感的なので、スマホに不慣れな方でも簡単に操作できます。文字サイズの調整も容易で、視力の弱い方にも配慮されています。また、緊急SOS機能も搭載されているので安心です。家族間の通話やメッセージのやり取りがスムーズになりました。",
        "helpful_votes": 27,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "SP-100",
        "product_name": "TechX Phone Pro",
        "review_id": "R013",
        "customer_id": "C1013",
        "rating": 1,
        "date": "2023-10-10",
        "title": "カスタマーサポートに失望",
        "text": "製品自体は悪くないのですが、不具合が発生した際のカスタマーサポートの対応が最悪でした。何度問い合わせても形式的な返答ばかりで、問題解決に至りませんでした。最終的には自分で解決策を見つけました。これだけ高価な製品を販売しているなら、サポート体制をもっと充実させるべきです。",
        "helpful_votes": 38,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "SP-100",
        "product_name": "TechX Phone Pro",
        "review_id": "R014",
        "customer_id": "C1014",
        "rating": 4,
        "date": "2023-07-20",
        "title": "アップデートで改善",
        "text": "購入当初はいくつか不満点がありましたが、最近のソフトウェアアップデートでほとんどの問題が解決されました。特にカメラアプリの使い勝手が大幅に向上し、新機能も追加されて楽しめます。メーカーが継続的に改善を続ける姿勢は評価できます。今後のアップデートにも期待しています。",
        "helpful_votes": 22,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "SP-100",
        "product_name": "TechX Phone Pro",
        "review_id": "R015",
        "customer_id": "C1015",
        "rating": 5,
        "date": "2023-09-15",
        "title": "完璧な一台",
        "text": "スマートフォンに求める全ての要素を満たしています。バッテリー持ちが良く、カメラ性能も申し分なく、処理速度も高速です。特に気に入っているのは顔認証の精度で、マスクをしていても素早く認識してくれます。防水性能も信頼できるレベルで、雨の日でも安心して使えます。これ以上望むものはありません。",
        "helpful_votes": 35,
        "verified_purchase": True,
        "country": "日本",
    },
]

# ノートパソコン製品のレビューサンプル
LAPTOP_REVIEWS = [
    {
        "product_id": "LT-200",
        "product_name": "UltraBook Pro",
        "review_id": "R101",
        "customer_id": "C2001",
        "rating": 5,
        "date": "2023-08-10",
        "title": "プロ仕様のノートPC",
        "text": "デザイン業務で使用していますが、性能が素晴らしいです。重いソフトウェアも軽快に動作し、バッテリーも一日中持つので外出先での作業も安心です。キーボードの打ち心地も良く、長時間の作業でも疲れにくいです。液晶の色再現性も正確で、写真や動画編集にも最適です。",
        "helpful_votes": 40,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "LT-200",
        "product_name": "UltraBook Pro",
        "review_id": "R102",
        "customer_id": "C2002",
        "rating": 4,
        "date": "2023-07-15",
        "title": "軽量で持ち運びに便利",
        "text": "1.2kgという軽さが最大の魅力です。毎日通勤で持ち歩いていますが、負担を感じません。処理速度も十分で、オフィスソフトなら問題なく動作します。ただ、冷却ファンの音が時々気になることがあります。それでも薄型軽量で性能も良いので、ビジネスマンには最適な選択肢だと思います。",
        "helpful_votes": 25,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "LT-200",
        "product_name": "UltraBook Pro",
        "review_id": "R103",
        "customer_id": "C2003",
        "rating": 2,
        "date": "2023-09-05",
        "title": "拡張性に難あり",
        "text": "基本性能は悪くないのですが、USBポートが2つしかなく、SDカードスロットもないため、周辺機器を接続するのに不便を感じます。毎回ハブを持ち歩く必要があり、せっかくの軽量さが台無しです。また、RAMが本体に固定されていてアップグレードできないのも残念です。",
        "helpful_votes": 30,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "LT-200",
        "product_name": "UltraBook Pro",
        "review_id": "R104",
        "customer_id": "C2004",
        "rating": 5,
        "date": "2023-08-25",
        "title": "バッテリー持ちが素晴らしい",
        "text": "出張が多い仕事なので、バッテリー持ちを重視して購入しましたが、期待以上の性能でした。Wi-Fi接続で通常の業務なら12時間以上持ちます。充電も高速で、30分で50%まで回復するのが便利です。処理性能も十分で、複数のアプリを同時に動かしても問題ありません。持ち運びにも便利な軽さです。",
        "helpful_votes": 33,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "LT-200",
        "product_name": "UltraBook Pro",
        "review_id": "R105",
        "customer_id": "C2005",
        "rating": 3,
        "date": "2023-07-30",
        "title": "キーボードに不満",
        "text": "全体的な性能は良いのですが、キーボードのキーストロークが浅すぎて長文入力が快適ではありません。また、一部のキーの反応が悪く、何度か押さないと入力されないことがあります。タッチパッドの精度は素晴らしいので、キーボードの品質も同レベルであれば完璧だったと思います。",
        "helpful_votes": 18,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "LT-200",
        "product_name": "UltraBook Pro",
        "review_id": "R106",
        "customer_id": "C2006",
        "rating": 1,
        "date": "2023-09-10",
        "title": "初期不良で返品",
        "text": "届いてすぐに電源が入らない症状が発生しました。充電しても改善せず、サポートに問い合わせたところ初期不良と診断されました。交換対応はスムーズでしたが、代替機も1週間ほどで同様の症状が現れ、再度返品しました。品質管理に問題があるのではないでしょうか。",
        "helpful_votes": 45,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "LT-200",
        "product_name": "UltraBook Pro",
        "review_id": "R107",
        "customer_id": "C2007",
        "rating": 4,
        "date": "2023-08-20",
        "title": "ディスプレイが美しい",
        "text": "4K対応の高精細ディスプレイが最大の魅力です。色鮮やかで視野角も広く、写真や動画の編集作業が捗ります。タッチスクリーン対応なのも便利で、直感的な操作が可能です。唯一の欠点は、高精細ディスプレイのためバッテリー消費が早いことです。それでも映像作業をする人にはおすすめできます。",
        "helpful_votes": 27,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "LT-200",
        "product_name": "UltraBook Pro",
        "review_id": "R108",
        "customer_id": "C2008",
        "rating": 5,
        "date": "2023-09-15",
        "title": "静音性が高い",
        "text": "以前使用していたノートPCはファンの音がうるさく、会議中に使用するのが恥ずかしいほどでした。しかしこの製品は驚くほど静かで、重い処理をしていても騒音レベルが低いです。発熱も少なく、長時間使用しても快適です。性能とのバランスを考えると、冷却システムの設計が非常に優れていると感じます。",
        "helpful_votes": 22,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "LT-200",
        "product_name": "UltraBook Pro",
        "review_id": "R109",
        "customer_id": "C2009",
        "rating": 2,
        "date": "2023-07-25",
        "title": "WEBカメラの品質が低い",
        "text": "テレワークでビデオ会議を頻繁に行いますが、内蔵WEBカメラの画質が非常に悪く、暗い環境ではほとんど使い物になりません。この価格帯の製品としては明らかに見劣りします。結局、外付けのWEBカメラを購入することになり、余計な出費となりました。カメラ以外の性能は悪くないだけに残念です。",
        "helpful_votes": 35,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "LT-200",
        "product_name": "UltraBook Pro",
        "review_id": "R110",
        "customer_id": "C2010",
        "rating": 4,
        "date": "2023-09-20",
        "title": "コスパ良好",
        "text": "同等スペックの他社製品と比較すると、2〜3万円安く購入できました。性能も十分で、日常的な作業からちょっとした動画編集まで問題なくこなせます。デザインもスタイリッシュで気に入っています。強いて言えば、スピーカーの音質がもう少し良ければ完璧でした。総合的には非常に満足しています。",
        "helpful_votes": 19,
        "verified_purchase": True,
        "country": "日本",
    },
]

# ワイヤレスイヤホン製品のレビューサンプル
EARPHONE_REVIEWS = [
    {
        "product_id": "EP-300",
        "product_name": "SoundPods Pro",
        "review_id": "R201",
        "customer_id": "C3001",
        "rating": 5,
        "date": "2023-08-05",
        "title": "ノイズキャンセリングが素晴らしい",
        "text": "通勤電車で使用していますが、ノイズキャンセリング機能が非常に優れています。周囲の騒音がほとんど聞こえなくなり、音楽に集中できます。バッテリー持続時間も長く、一回の充電で丸一日使えます。装着感も良く、長時間使用しても耳が痛くなりません。音質も非常にクリアで、特に中高音域の表現力が素晴らしいです。",
        "helpful_votes": 38,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "EP-300",
        "product_name": "SoundPods Pro",
        "review_id": "R202",
        "customer_id": "C3002",
        "rating": 4,
        "date": "2023-07-20",
        "title": "コスパ最高のワイヤレスイヤホン",
        "text": "有名ブランドの半額以下で、ほぼ同等の性能が得られるのは驚きです。音質は特に低音が豊かで、ロックやEDMを聴くのに最適です。接続も安定していて、途切れることはほとんどありません。唯一気になる点は、ケースがやや大きく、ポケットに入れると膨らんでしまうことです。それでも総合的には大満足です。",
        "helpful_votes": 25,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "EP-300",
        "product_name": "SoundPods Pro",
        "review_id": "R203",
        "customer_id": "C3003",
        "rating": 2,
        "date": "2023-09-10",
        "title": "接続が不安定",
        "text": "音質自体は良いのですが、Bluetooth接続が非常に不安定です。特に混雑した場所では頻繁に音が途切れ、ストレスを感じます。また、左右のイヤホン間の接続も時々切れることがあり、不便です。ファームウェアのアップデートで改善されることを期待していますが、現状では残念ながらおすすめできません。",
        "helpful_votes": 32,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "EP-300",
        "product_name": "SoundPods Pro",
        "review_id": "R204",
        "customer_id": "C3004",
        "rating": 5,
        "date": "2023-08-15",
        "title": "通話品質が優れている",
        "text": "テレワークでのビデオ会議用に購入しましたが、マイク性能が非常に優れています。周囲の雑音を効果的に除去し、クリアな音声を届けてくれます。また、装着感も良く、長時間の会議でも疲れません。音楽再生時の音質も素晴らしく、仕事とプライベート両方で活躍しています。防水性能もあり、軽い雨の日も安心です。",
        "helpful_votes": 29,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "EP-300",
        "product_name": "SoundPods Pro",
        "review_id": "R205",
        "customer_id": "C3005",
        "rating": 3,
        "date": "2023-07-25",
        "title": "フィット感に個人差あり",
        "text": "音質やバッテリー持続時間は満足していますが、私の耳には合わず、少し動くだけでずれてしまいます。付属のイヤーピースを全て試しましたが、しっくりくるものがありませんでした。サードパーティ製のイヤーピースを購入して改善しましたが、最初から複数のタイプが付属していればより良かったと思います。",
        "helpful_votes": 20,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "EP-300",
        "product_name": "SoundPods Pro",
        "review_id": "R206",
        "customer_id": "C3006",
        "rating": 1,
        "date": "2023-09-20",
        "title": "すぐに片方が聞こえなくなった",
        "text": "購入から2週間で右側のイヤホンから音が出なくなりました。充電はされているようですが、音楽を再生しても無音です。カスタマーサポートに連絡しましたが、返品・交換手続きが複雑で時間がかかります。この価格帯の製品としては品質管理に問題があると感じます。非常に残念です。",
        "helpful_votes": 40,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "EP-300",
        "product_name": "SoundPods Pro",
        "review_id": "R207",
        "customer_id": "C3007",
        "rating": 4,
        "date": "2023-08-25",
        "title": "アプリの使い勝手が良い",
        "text": "専用アプリが非常に使いやすく、イコライザー設定やノイズキャンセリングレベルの調整が簡単にできます。また、イヤホンを紛失した際に位置を特定する機能も役立ちます。音質も十分満足していますが、高音域がやや強調されすぎているように感じることがあります。アプリでの調整で改善できますが、デフォルト設定がもう少しバランスが良ければ完璧でした。",
        "helpful_votes": 22,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "EP-300",
        "product_name": "SoundPods Pro",
        "review_id": "R208",
        "customer_id": "C3008",
        "rating": 5,
        "date": "2023-09-15",
        "title": "バッテリー持続時間が素晴らしい",
        "text": "一回の充電で8時間以上使用でき、ケースを合わせると30時間以上使えるのが非常に便利です。旅行中も充電の心配をせずに使用できました。急速充電にも対応しており、10分の充電で2時間使えるのも魅力です。音質も期待以上で、特に解像度の高さに驚きました。この価格帯では間違いなく最高の選択肢だと思います。",
        "helpful_votes": 35,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "EP-300",
        "product_name": "SoundPods Pro",
        "review_id": "R209",
        "customer_id": "C3009",
        "rating": 3,
        "date": "2023-08-10",
        "title": "タッチコントロールの反応に難あり",
        "text": "音質とノイズキャンセリング性能は良いのですが、タッチコントロールの精度が低く、意図しない操作が頻繁に発生します。特に運動中は誤操作が多く、ストレスを感じます。また、タッチ操作のカスタマイズができないのも残念です。ボタン式の方が個人的には使いやすかったと思います。それ以外の面では満足しています。",
        "helpful_votes": 28,
        "verified_purchase": True,
        "country": "日本",
    },
    {
        "product_id": "EP-300",
        "product_name": "SoundPods Pro",
        "review_id": "R210",
        "customer_id": "C3010",
        "rating": 4,
        "date": "2023-09-25",
        "title": "マルチポイント接続が便利",
        "text": "2台のデバイスに同時に接続できるマルチポイント機能が非常に便利です。仕事用のPCと個人のスマホを行き来する必要がある私にとって、接続し直す手間が省けるのは大きなメリットです。音質も十分満足でき、特に音場の広さが気に入っています。唯一改善してほしいのは、ケースのワイヤレス充電に対応してほしいということです。",
        "helpful_votes": 19,
        "verified_purchase": True,
        "country": "日本",
    },
]


def get_all_reviews():
    """全ての製品レビューを取得します。"""
    return SMARTPHONE_REVIEWS + LAPTOP_REVIEWS + EARPHONE_REVIEWS


def get_product_reviews(product_id=None):
    """指定された製品IDのレビューを取得します。製品IDが指定されていない場合は、全ての製品のレビューを返します。"""
    all_reviews = get_all_reviews()

    if product_id is None:
        return all_reviews

    return [review for review in all_reviews if review["product_id"] == product_id]


def get_reviews_by_rating(min_rating=None, max_rating=None):
    """評価点の範囲でレビューをフィルタリングします。"""
    all_reviews = get_all_reviews()

    if min_rating is None and max_rating is None:
        return all_reviews

    filtered_reviews = all_reviews

    if min_rating is not None:
        filtered_reviews = [
            review for review in filtered_reviews if review["rating"] >= min_rating
        ]

    if max_rating is not None:
        filtered_reviews = [
            review for review in filtered_reviews if review["rating"] <= max_rating
        ]

    return filtered_reviews


def get_reviews_by_date_range(start_date=None, end_date=None):
    """日付範囲でレビューをフィルタリングします。"""
    all_reviews = get_all_reviews()

    if start_date is None and end_date is None:
        return all_reviews

    filtered_reviews = all_reviews

    if start_date is not None:
        filtered_reviews = [
            review for review in filtered_reviews if review["date"] >= start_date
        ]

    if end_date is not None:
        filtered_reviews = [
            review for review in filtered_reviews if review["date"] <= end_date
        ]

    return filtered_reviews


def search_reviews(query):
    """レビューテキスト内でキーワード検索を行います。"""
    all_reviews = get_all_reviews()

    if not query:
        return all_reviews

    query = query.lower()
    return [
        review
        for review in all_reviews
        if query in review["title"].lower() or query in review["text"].lower()
    ]
