import pandas as pd
import numpy as np
from utils.data_generators import load_dataset
import openai


# データ分析関数
def analyze_data(dataset_name, client, specific_query=None):
    df = load_dataset(dataset_name)

    # 基本的な統計情報の抽出
    stats = {}
    explanations = []

    try:
        if dataset_name == "population":
            # 最新年のデータ
            latest_year = df["年"].max()
            total_population = df[df["年"] == latest_year]["総人口"].sum()
            avg_population = df[df["年"] == latest_year]["総人口"].mean()

            # 人口の多い上位5都道府県
            top_prefectures = (
                df[df["年"] == latest_year]
                .sort_values("総人口", ascending=False)["都道府県"]
                .head(5)
                .tolist()
            )

            # 年齢構成比
            age_groups = df[df["年"] == latest_year][
                ["0-14歳", "15-64歳", "65歳以上"]
            ].sum()
            age_ratio = age_groups / age_groups.sum()

            # 人口増減率（最初の年と最新の年を比較）
            first_year = df["年"].min()
            pop_change = df.groupby("年")["総人口"].sum()
            pop_change_rate = (
                (pop_change[latest_year] - pop_change[first_year])
                / pop_change[first_year]
                * 100
            )

            stats = {
                "latest_year": int(latest_year),
                "total_population": int(total_population),
                "avg_prefecture_population": int(avg_population),
                "top_prefectures": top_prefectures,
                "age_ratio": {
                    "0-14歳": f"{age_ratio['0-14歳']*100:.1f}%",
                    "15-64歳": f"{age_ratio['15-64歳']*100:.1f}%",
                    "65歳以上": f"{age_ratio['65歳以上']*100:.1f}%",
                },
                "population_change_rate": f"{pop_change_rate:.1f}%",
            }

        elif dataset_name == "weather":
            # 最新年のデータ
            latest_year = df["年"].max()
            latest_data = df[df["年"] == latest_year]

            # 最高・最低気温の都市
            hottest_city = latest_data.groupby("都市")["平均気温(°C)"].mean().idxmax()
            coldest_city = latest_data.groupby("都市")["平均気温(°C)"].mean().idxmin()

            # 降水量が最も多い・少ない都市
            wettest_city = latest_data.groupby("都市")["降水量(mm)"].sum().idxmax()
            driest_city = latest_data.groupby("都市")["降水量(mm)"].sum().idxmin()

            # 気温の上昇トレンド
            temp_trend = df.groupby("年")["平均気温(°C)"].mean()
            temp_change = temp_trend[latest_year] - temp_trend[df["年"].min()]

            stats = {
                "latest_year": int(latest_year),
                "hottest_city": hottest_city,
                "coldest_city": coldest_city,
                "hottest_city_temp": f"{latest_data[latest_data['都市']==hottest_city]['平均気温(°C)'].mean():.1f}°C",
                "coldest_city_temp": f"{latest_data[latest_data['都市']==coldest_city]['平均気温(°C)'].mean():.1f}°C",
                "wettest_city": wettest_city,
                "driest_city": driest_city,
                "wettest_city_precip": f"{latest_data[latest_data['都市']==wettest_city]['降水量(mm)'].sum():.1f}mm",
                "driest_city_precip": f"{latest_data[latest_data['都市']==driest_city]['降水量(mm)'].sum():.1f}mm",
                "temp_change": f"{temp_change:.2f}°C",
            }

        elif dataset_name == "energy":
            # 最新年のデータ
            latest_year = df["年"].max()
            latest_data = df[df["年"] == latest_year]

            # エネルギー源別の割合
            total_energy = latest_data["発電量(TWh)"].sum()
            energy_share = {
                source: f"{value/total_energy*100:.1f}%"
                for source, value in zip(
                    latest_data["エネルギー源"], latest_data["発電量(TWh)"]
                )
            }

            # 再生可能エネルギーの割合
            renewable_sources = ["水力", "太陽光", "風力", "バイオマス"]
            renewable_energy = latest_data[
                latest_data["エネルギー源"].isin(renewable_sources)
            ]["発電量(TWh)"].sum()
            renewable_share = renewable_energy / total_energy * 100

            # 化石燃料への依存度
            fossil_sources = ["石炭", "石油", "天然ガス"]
            fossil_energy = latest_data[
                latest_data["エネルギー源"].isin(fossil_sources)
            ]["発電量(TWh)"].sum()
            fossil_share = fossil_energy / total_energy * 100

            # 過去10年間の変化
            past_year = latest_year - 10
            past_data = (
                df[df["年"] == past_year]
                if past_year in df["年"].unique()
                else df[df["年"] == df["年"].min()]
            )

            # 過去と比較した際の再生可能エネルギーの成長率
            past_renewable = past_data[
                past_data["エネルギー源"].isin(renewable_sources)
            ]["発電量(TWh)"].sum()
            renewable_growth = (
                (renewable_energy - past_renewable) / past_renewable * 100
                if past_renewable > 0
                else 100
            )

            stats = {
                "latest_year": int(latest_year),
                "total_energy": f"{total_energy:.1f} TWh",
                "energy_share": energy_share,
                "renewable_share": f"{renewable_share:.1f}%",
                "fossil_share": f"{fossil_share:.1f}%",
                "renewable_growth_10yr": f"{renewable_growth:.1f}%",
            }

        elif dataset_name == "transport":
            # 最新年のデータ
            latest_year = df["年"].max()
            latest_data = df[df["年"] == latest_year]

            # 交通手段別の利用割合
            total_transport = latest_data["輸送人員(百万人)"].sum()
            transport_share = (
                latest_data.groupby("交通手段")["輸送人員(百万人)"].sum()
                / total_transport
                * 100
            )

            # 地域別の公共交通利用割合
            public_transport = ["鉄道", "バス", "タクシー", "航空", "船舶"]

            region_transport = {}
            for region in latest_data["地域"].unique():
                region_data = latest_data[latest_data["地域"] == region]
                total_region = region_data["輸送人員(百万人)"].sum()
                public_region = region_data[
                    region_data["交通手段"].isin(public_transport)
                ]["輸送人員(百万人)"].sum()
                region_transport[region] = public_region / total_region * 100

            # 過去10年間の交通手段変化
            past_year = latest_year - 10
            past_data = (
                df[df["年"] == past_year]
                if past_year in df["年"].unique()
                else df[df["年"] == df["年"].min()]
            )

            transport_change = {}
            for transport in df["交通手段"].unique():
                latest_value = latest_data[latest_data["交通手段"] == transport][
                    "輸送人員(百万人)"
                ].sum()
                past_value = past_data[past_data["交通手段"] == transport][
                    "輸送人員(百万人)"
                ].sum()
                change = (latest_value - past_value) / past_value * 100
                transport_change[transport] = f"{change:.1f}%"

            stats = {
                "latest_year": int(latest_year),
                "total_transport": f"{total_transport:.1f} 百万人",
                "transport_share": {t: f"{v:.1f}%" for t, v in transport_share.items()},
                "public_transport_by_region": {
                    r: f"{v:.1f}%" for r, v in region_transport.items()
                },
                "transport_change_10yr": transport_change,
            }

    except Exception as e:
        print(f"Error analyzing data: {str(e)}")
        stats = {"error": str(e)}

    # AI解析を取得
    if specific_query:
        explanations = generate_ai_explanation(dataset_name, df, client, specific_query)
    else:
        explanations = generate_ai_explanation(dataset_name, df, client)

    return stats, explanations


# OpenAI APIを用いたデータ解析
def generate_ai_explanation(dataset_name, df, client, specific_query=None):
    # データセットの概要を作成
    if dataset_name == "population":
        data_summary = f"""
        このデータセットは日本の人口統計データです。
        期間: {df['年'].min()}年から{df['年'].max()}年
        都道府県数: {df['都道府県'].nunique()}
        データ内容: 都道府県別の総人口と年齢層別（0-14歳、15-64歳、65歳以上）の人口
        """
    elif dataset_name == "weather":
        data_summary = f"""
        このデータセットは日本の主要都市の気象データです。
        期間: {df['年'].min()}年から{df['年'].max()}年
        都市数: {df['都市'].nunique()}
        データ内容: 都市別の月間平均気温と降水量
        """
    elif dataset_name == "energy":
        data_summary = f"""
        このデータセットは日本のエネルギー生産データです。
        期間: {df['年'].min()}年から{df['年'].max()}年
        エネルギー源: {', '.join(df['エネルギー源'].unique())}
        データ内容: エネルギー源別の年間発電量（TWh）
        """
    elif dataset_name == "transport":
        data_summary = f"""
        このデータセットは日本の交通輸送データです。
        期間: {df['年'].min()}年から{df['年'].max()}年
        交通手段: {', '.join(df['交通手段'].unique())}
        地域区分: {', '.join(df['地域'].unique())}
        データ内容: 地域別・交通手段別の年間輸送人員（百万人）
        """

    # 基本的な統計情報
    data_stats = df.describe().to_string()

    # クエリがない場合の標準的な質問
    if not specific_query:
        if dataset_name == "population":
            query = """
            以下の視点からデータを分析してください：
            1. 日本の人口動向の全体的なトレンドは？
            2. 高齢化の進行状況とその地域差は？
            3. 人口減少が最も著しい地域とその理由は？
            4. 都市部と地方の人口変動の違いは？
            5. 今後予想される人口構造の変化とその影響は？
            """
        elif dataset_name == "weather":
            query = """
            以下の視点からデータを分析してください：
            1. 日本の気温変動の全体的なトレンドは？
            2. 地域別の気候パターンの特徴は？
            3. 過去数年間で最も気候変動が顕著な都市は？
            4. 降水量パターンの変化とその影響は？
            5. 気象データから見える環境変化の兆候は？
            """
        elif dataset_name == "energy":
            query = """
            以下の視点からデータを分析してください：
            1. 日本のエネルギー構成の変遷は？
            2. 再生可能エネルギーの成長率とその背景は？
            3. 原子力発電の変動とその影響は？
            4. 化石燃料依存度の変化は？
            5. エネルギー転換の進捗状況と課題は？
            """
        elif dataset_name == "transport":
            query = """
            以下の視点からデータを分析してください：
            1. 日本の交通手段利用の全体的なトレンドは？
            2. 地域による交通手段の違いとその背景は？
            3. 公共交通機関の利用状況の変化は？
            4. 自家用車依存度の変化とその要因は？
            5. 新型コロナウイルスの影響と今後の交通パターンの変化の見通しは？
            """
    else:
        query = specific_query

    try:
        # OpenAI APIを使用してデータ解析
        prompt = f"""
        あなたは公共データ分析の専門家です。以下のデータセットを分析し、洞察を提供してください。

        【データセット概要】
        {data_summary}

        【分析内容】
        {query}

        簡潔かつ分かりやすく説明し、重要なポイントを箇条書きでまとめてください。
        データの傾向、パターン、特異点などに注目し、可能な限り具体的な数値や比較を含めてください。
        """

        # APIリクエスト
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "あなたは公共データ分析の専門家です。データに基づいた客観的で正確な分析を提供してください。マークダウン形式で回答してください。見出しや箇条書きを活用して、読みやすく構造化された回答を作成してください。",
                },
                {"role": "user", "content": prompt + "\n\nマークダウン形式で回答してください。見出し(#)、箇条書き(-)、強調(**太字**)などを適切に使用してください。"},
            ],
            temperature=0.5,
        )

        # レスポンスを取得
        explanation = response.choices[0].message.content
        return explanation

    except Exception as e:
        return f"データ分析中にエラーが発生しました: {str(e)}"
