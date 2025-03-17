import numpy as np
import pandas as pd
import os


# 人口データの生成
def generate_population_data():
    prefectures = [
        "北海道",
        "青森県",
        "岩手県",
        "宮城県",
        "秋田県",
        "山形県",
        "福島県",
        "茨城県",
        "栃木県",
        "群馬県",
        "埼玉県",
        "千葉県",
        "東京都",
        "神奈川県",
        "新潟県",
        "富山県",
        "石川県",
        "福井県",
        "山梨県",
        "長野県",
        "岐阜県",
        "静岡県",
        "愛知県",
        "三重県",
        "滋賀県",
        "京都府",
        "大阪府",
        "兵庫県",
        "奈良県",
        "和歌山県",
        "鳥取県",
        "島根県",
        "岡山県",
        "広島県",
        "山口県",
        "徳島県",
        "香川県",
        "愛媛県",
        "高知県",
        "福岡県",
        "佐賀県",
        "長崎県",
        "熊本県",
        "大分県",
        "宮崎県",
        "鹿児島県",
        "沖縄県",
    ]

    years = list(range(2010, 2023))

    data = []

    # 各都道府県のデータを生成
    for prefecture in prefectures:
        # 2010年の基準人口を設定（地域ごとに異なる）
        base_population = np.random.randint(500000, 5000000)
        if prefecture in [
            "東京都",
            "大阪府",
            "神奈川県",
            "愛知県",
            "埼玉県",
            "千葉県",
            "兵庫県",
            "福岡県",
        ]:
            base_population = np.random.randint(3000000, 13000000)

        # 地域ごとのトレンド
        if prefecture in ["東京都", "神奈川県", "埼玉県", "千葉県", "愛知県", "大阪府"]:
            trend = np.random.uniform(0.002, 0.01, len(years))  # 都市部は人口増加傾向
        elif prefecture in [
            "北海道",
            "青森県",
            "秋田県",
            "山形県",
            "和歌山県",
            "島根県",
            "高知県",
        ]:
            trend = np.random.uniform(-0.015, -0.005, len(years))  # 地方は人口減少傾向
        else:
            trend = np.random.uniform(-0.008, 0.004, len(years))  # その他はやや減少傾向

        # 年齢層別データの基準値
        age_groups = {
            "0-14歳": np.random.uniform(0.11, 0.15),
            "15-64歳": np.random.uniform(0.55, 0.65),
            "65歳以上": np.random.uniform(0.20, 0.35),
        }

        # 地域特性を反映
        if prefecture in ["東京都", "神奈川県", "大阪府", "愛知県"]:
            age_groups["0-14歳"] *= 0.9  # 都市部は子供が少ない
            age_groups["15-64歳"] *= 1.1  # 労働人口が多い
            age_groups["65歳以上"] *= 0.85  # 高齢者が少ない
        elif prefecture in ["秋田県", "島根県", "山形県", "高知県"]:
            age_groups["0-14歳"] *= 0.8  # 地方は子供が少ない
            age_groups["15-64歳"] *= 0.9  # 労働人口が少ない
            age_groups["65歳以上"] *= 1.2  # 高齢者が多い

        # 各年のデータを生成
        for i, year in enumerate(years):
            # 人口変動のトレンドを適用
            if i > 0:
                base_population = base_population * (1 + trend[i])

                # 年齢層の変動（年々高齢化）
                age_groups["0-14歳"] -= 0.002
                age_groups["15-64歳"] -= 0.004
                age_groups["65歳以上"] += 0.006

            population = int(base_population)

            # 年齢層別の人口を計算
            population_0_14 = int(population * age_groups["0-14歳"])
            population_15_64 = int(population * age_groups["15-64歳"])
            population_65_plus = int(population * age_groups["65歳以上"])

            # データを追加
            data.append(
                {
                    "年": year,
                    "都道府県": prefecture,
                    "総人口": population,
                    "0-14歳": population_0_14,
                    "15-64歳": population_15_64,
                    "65歳以上": population_65_plus,
                }
            )

    return pd.DataFrame(data)


# 気象データの生成
def generate_weather_data():
    cities = [
        "札幌",
        "仙台",
        "東京",
        "横浜",
        "新潟",
        "金沢",
        "名古屋",
        "京都",
        "大阪",
        "神戸",
        "広島",
        "高松",
        "福岡",
        "鹿児島",
        "那覇",
    ]

    months = [
        "1月",
        "2月",
        "3月",
        "4月",
        "5月",
        "6月",
        "7月",
        "8月",
        "9月",
        "10月",
        "11月",
        "12月",
    ]

    years = list(range(2018, 2023))

    data = []

    # 各都市の基準気温と降水量
    base_temps = {
        "札幌": [-3.6, -3.1, 0.6, 7.1, 12.4, 16.7, 20.5, 22.3, 18.1, 11.8, 4.9, -0.9],
        "仙台": [1.6, 2.1, 5.2, 10.3, 15.2, 19.5, 23.2, 24.8, 21.2, 15.4, 9.1, 4.0],
        "東京": [5.2, 5.7, 8.7, 13.9, 18.2, 21.4, 25.0, 26.4, 23.2, 17.8, 12.1, 7.6],
        "横浜": [5.7, 6.0, 9.0, 14.2, 18.5, 21.7, 25.3, 26.7, 23.5, 18.1, 12.5, 8.1],
        "新潟": [2.8, 2.8, 5.8, 11.4, 16.4, 20.5, 24.5, 25.9, 21.8, 15.9, 10.0, 5.2],
        "金沢": [3.6, 3.9, 7.0, 12.4, 17.0, 21.2, 24.9, 26.3, 22.5, 16.6, 11.1, 6.4],
        "名古屋": [4.5, 5.2, 8.5, 14.0, 18.7, 22.7, 26.4, 27.8, 24.2, 18.2, 12.2, 7.3],
        "京都": [4.6, 5.1, 8.6, 14.3, 19.0, 22.9, 26.8, 28.2, 24.3, 18.1, 12.1, 7.3],
        "大阪": [6.0, 6.4, 9.6, 15.1, 19.6, 23.5, 27.4, 28.8, 25.1, 19.0, 13.2, 8.5],
        "神戸": [6.1, 6.6, 9.7, 15.0, 19.3, 23.0, 26.8, 28.2, 24.8, 19.0, 13.3, 8.6],
        "広島": [5.3, 5.8, 9.0, 14.2, 18.8, 22.7, 26.4, 27.7, 24.0, 18.2, 12.4, 7.7],
        "高松": [5.6, 6.2, 9.5, 14.7, 19.1, 22.9, 26.7, 27.9, 24.2, 18.5, 12.8, 8.0],
        "福岡": [6.6, 7.4, 10.4, 15.1, 19.4, 23.0, 27.0, 28.1, 24.4, 19.0, 13.5, 8.9],
        "鹿児島": [
            8.9,
            9.8,
            12.6,
            16.9,
            20.8,
            24.0,
            28.0,
            28.6,
            25.7,
            20.7,
            15.3,
            10.8,
        ],
        "那覇": [
            16.6,
            16.8,
            18.9,
            21.4,
            24.0,
            26.8,
            28.9,
            28.7,
            27.6,
            25.2,
            21.7,
            18.5,
        ],
    }

    base_precip = {
        "札幌": [113, 94, 77, 56, 57, 46, 81, 123, 128, 108, 104, 111],
        "仙台": [37, 48, 86, 94, 98, 140, 164, 148, 181, 90, 68, 45],
        "東京": [52, 56, 100, 124, 128, 164, 161, 155, 209, 163, 92, 51],
        "横浜": [64, 60, 114, 126, 132, 167, 161, 139, 219, 164, 96, 57],
        "新潟": [186, 132, 107, 85, 89, 93, 177, 152, 137, 129, 193, 226],
        "金沢": [299, 199, 153, 131, 122, 146, 202, 138, 179, 156, 250, 296],
        "名古屋": [48, 66, 110, 124, 156, 198, 210, 177, 208, 129, 79, 50],
        "京都": [50, 66, 110, 127, 150, 201, 226, 145, 204, 120, 75, 47],
        "大阪": [45, 61, 104, 103, 145, 186, 157, 100, 160, 112, 69, 44],
        "神戸": [48, 62, 100, 106, 138, 194, 156, 108, 160, 109, 67, 45],
        "広島": [44, 63, 112, 136, 158, 248, 237, 110, 181, 84, 65, 37],
        "高松": [39, 53, 84, 106, 112, 196, 144, 84, 133, 70, 55, 31],
        "福岡": [68, 72, 110, 119, 145, 250, 252, 164, 171, 87, 85, 57],
        "鹿児島": [78, 106, 162, 189, 217, 428, 265, 253, 206, 101, 93, 77],
        "那覇": [107, 120, 161, 166, 232, 247, 142, 240, 261, 153, 110, 103],
    }

    # 各都市、各月、各年のデータを生成
    for city in cities:
        for year in years:
            for i, month in enumerate(months):
                # 年ごと、月ごとの変動を加える
                temp_variation = np.random.normal(0, 1.0)  # 気温の自然変動
                precip_variation = np.random.normal(1.0, 0.25)  # 降水量の自然変動

                # 気候変動の影響（年が進むにつれて気温が上昇）
                climate_change = (year - 2018) * 0.03

                # 基準値に変動を適用
                avg_temp = base_temps[city][i] + temp_variation + climate_change
                precipitation = max(0, base_precip[city][i] * precip_variation)

                # データを追加
                data.append(
                    {
                        "年": year,
                        "月": month,
                        "都市": city,
                        "平均気温(°C)": round(avg_temp, 1),
                        "降水量(mm)": round(precipitation, 1),
                    }
                )

    return pd.DataFrame(data)


# データセットの生成と保存
def initialize_datasets():
    os.makedirs("showroom/usecase-045/static/data", exist_ok=True)

    # 人口データ
    population_df = generate_population_data()
    population_df.to_csv(
        "showroom/usecase-045/static/data/population_data.csv", index=False
    )

    # 気象データ
    weather_df = generate_weather_data()
    weather_df.to_csv("showroom/usecase-045/static/data/weather_data.csv", index=False)

    # エネルギーと交通データは別ファイルから生成
    from utils.data_generators_extra import (
        generate_energy_data,
        generate_transport_data,
    )

    # エネルギーデータ
    energy_df = generate_energy_data()
    energy_df.to_csv("showroom/usecase-045/static/data/energy_data.csv", index=False)

    # 交通データ
    transport_df = generate_transport_data()
    transport_df.to_csv(
        "showroom/usecase-045/static/data/transport_data.csv", index=False
    )


# データの読み込み
def load_dataset(dataset_name):
    file_path = f"showroom/usecase-045/static/data/{dataset_name}_data.csv"

    if not os.path.exists(file_path):
        initialize_datasets()

    return pd.read_csv(file_path)
