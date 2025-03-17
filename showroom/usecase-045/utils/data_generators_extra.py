import numpy as np
import pandas as pd


# エネルギーデータの生成
def generate_energy_data():
    years = list(range(2010, 2023))
    sources = [
        "石炭",
        "石油",
        "天然ガス",
        "原子力",
        "水力",
        "太陽光",
        "風力",
        "バイオマス",
    ]

    data = []

    # 各年のエネルギー源別データを生成
    for year in years:
        # 基準値（2010年時点）
        if year == 2010:
            coal = 280  # TWh
            oil = 100
            gas = 330
            nuclear = 290
            hydro = 90
            solar = 3
            wind = 5
            biomass = 22
        else:
            # 前年のデータを取得
            prev_data = [d for d in data if d["年"] == year - 1]

            # 各エネルギー源の変化率を設定
            # 政策変更や技術発展を反映
            if year < 2011:  # 東日本大震災前
                coal_change = np.random.uniform(-0.01, 0.02)
                oil_change = np.random.uniform(-0.03, -0.01)
                gas_change = np.random.uniform(0.01, 0.03)
                nuclear_change = np.random.uniform(-0.01, 0.01)
                hydro_change = np.random.uniform(-0.02, 0.02)
                solar_change = np.random.uniform(0.10, 0.20)
                wind_change = np.random.uniform(0.05, 0.10)
                biomass_change = np.random.uniform(0.03, 0.08)
            elif year < 2015:  # 震災後、再生可能エネルギー促進
                coal_change = np.random.uniform(0.02, 0.05)  # 原発代替で増加
                oil_change = np.random.uniform(-0.02, 0.02)
                gas_change = np.random.uniform(0.03, 0.06)  # 原発代替で増加
                nuclear_change = (
                    np.random.uniform(-0.8, -0.6)
                    if year == 2011
                    else np.random.uniform(-0.2, 0)
                )
                hydro_change = np.random.uniform(-0.02, 0.02)
                solar_change = np.random.uniform(0.50, 0.80)  # FIT制度で急増
                wind_change = np.random.uniform(0.10, 0.15)
                biomass_change = np.random.uniform(0.05, 0.10)
            else:  # 2015年以降、脱炭素の流れ
                coal_change = np.random.uniform(-0.04, -0.01)  # 脱石炭の流れ
                oil_change = np.random.uniform(-0.04, -0.02)
                gas_change = np.random.uniform(-0.02, 0.02)
                nuclear_change = (
                    np.random.uniform(0.05, 0.15) if year > 2015 else 0
                )  # 一部再稼働
                hydro_change = np.random.uniform(-0.01, 0.01)
                solar_change = np.random.uniform(0.15, 0.25)  # 継続的に増加
                wind_change = np.random.uniform(0.15, 0.25)  # 洋上風力の増加
                biomass_change = np.random.uniform(0.05, 0.10)

            # 前年からの変化を適用
            coal = prev_data[0]["発電量(TWh)"] * (1 + coal_change)
            oil = prev_data[1]["発電量(TWh)"] * (1 + oil_change)
            gas = prev_data[2]["発電量(TWh)"] * (1 + gas_change)
            nuclear = prev_data[3]["発電量(TWh)"] * (1 + nuclear_change)
            hydro = prev_data[4]["発電量(TWh)"] * (1 + hydro_change)
            solar = prev_data[5]["発電量(TWh)"] * (1 + solar_change)
            wind = prev_data[6]["発電量(TWh)"] * (1 + wind_change)
            biomass = prev_data[7]["発電量(TWh)"] * (1 + biomass_change)

        # 各エネルギー源のデータを追加
        values = [coal, oil, gas, nuclear, hydro, solar, wind, biomass]
        for i, source in enumerate(sources):
            data.append(
                {"年": year, "エネルギー源": source, "発電量(TWh)": round(values[i], 1)}
            )

    return pd.DataFrame(data)


# 交通データの生成
def generate_transport_data():
    years = list(range(2010, 2023))
    transport_types = ["自家用車", "鉄道", "バス", "タクシー", "航空", "船舶"]
    regions = ["首都圏", "近畿圏", "中部圏", "その他地域"]

    data = []

    # 基準値（2010年、地域別、交通手段別の輸送人員（百万人））
    base_values = {
        "首都圏": {
            "自家用車": 4200,
            "鉄道": 7500,
            "バス": 1200,
            "タクシー": 650,
            "航空": 220,
            "船舶": 90,
        },
        "近畿圏": {
            "自家用車": 3100,
            "鉄道": 5200,
            "バス": 850,
            "タクシー": 450,
            "航空": 180,
            "船舶": 70,
        },
        "中部圏": {
            "自家用車": 2800,
            "鉄道": 2500,
            "バス": 580,
            "タクシー": 320,
            "航空": 150,
            "船舶": 50,
        },
        "その他地域": {
            "自家用車": 5200,
            "鉄道": 2300,
            "バス": 750,
            "タクシー": 520,
            "航空": 280,
            "船舶": 110,
        },
    }

    # 各年、地域、交通手段のデータを生成
    for year in years:
        for region in regions:
            year_idx = year - 2010

            for transport in transport_types:
                # 年ごとのトレンドを適用
                if transport == "自家用車":
                    if region in ["首都圏", "近畿圏"]:
                        trend = np.random.uniform(-0.015, -0.005)  # 都市部は車が減少
                    else:
                        trend = np.random.uniform(-0.005, 0.005)  # 地方は横ばい
                elif transport == "鉄道":
                    if region in ["首都圏", "近畿圏", "中部圏"]:
                        trend = np.random.uniform(0.005, 0.015)  # 都市部は鉄道が増加
                    else:
                        trend = np.random.uniform(-0.01, 0)  # 地方は鉄道が減少
                elif transport == "バス":
                    trend = np.random.uniform(-0.01, 0)  # 全体的に減少傾向
                elif transport == "タクシー":
                    if year >= 2018:  # 配車アプリの普及
                        trend = np.random.uniform(0, 0.01)
                    else:
                        trend = np.random.uniform(-0.01, 0)
                elif transport == "航空":
                    if year >= 2020 and year <= 2021:  # コロナの影響
                        trend = np.random.uniform(-0.6, -0.4)
                    else:
                        trend = np.random.uniform(0.01, 0.03)  # 通常は増加傾向
                elif transport == "船舶":
                    trend = np.random.uniform(-0.005, 0.005)  # ほぼ横ばい

                # 2011年は東日本大震災の影響
                if year == 2011:
                    disaster_impact = (
                        np.random.uniform(-0.15, -0.05)
                        if region in ["首都圏", "その他地域"]
                        else 0
                    )
                    trend += disaster_impact

                # 2020-2021年はコロナの影響
                if year in [2020, 2021]:
                    if transport in ["鉄道", "バス", "タクシー"]:
                        covid_impact = np.random.uniform(-0.4, -0.2)
                        trend += covid_impact

                # 基準値から計算
                base = base_values[region][transport]
                if year == 2010:
                    value = base
                else:
                    # 前年からの累積変化を計算
                    prev_data = [
                        d
                        for d in data
                        if d["年"] == year - 1
                        and d["地域"] == region
                        and d["交通手段"] == transport
                    ]
                    prev_value = prev_data[0]["輸送人員(百万人)"]
                    value = prev_value * (1 + trend)

                # データを追加
                data.append(
                    {
                        "年": year,
                        "地域": region,
                        "交通手段": transport,
                        "輸送人員(百万人)": round(value, 1),
                    }
                )

    return pd.DataFrame(data)
