import pandas as pd
import json
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.utils
import plotly.io as pio
from utils.data_generators import load_dataset

# NumPy配列をJSON化できるようにするカスタムエンコーダ
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super(NumpyEncoder, self).default(obj)

# Plotlyのデフォルトテーマとカラー設定
pio.templates.default = "plotly_white"

# 直接JSONオブジェクトを生成する関数
def create_visualizations(dataset_name, df):
    """データセットに基づいて可視化JSONを生成する関数"""
    # ブール値をJavaScript互換の文字列に変換する関数
    def convert_booleans_to_js(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, bool):
                    obj[key] = "true" if value else "false"
                elif isinstance(value, (dict, list)):
                    convert_booleans_to_js(value)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, bool):
                    obj[i] = "true" if item else "false"
                elif isinstance(item, (dict, list)):
                    convert_booleans_to_js(item)
        return obj
    
    visualizations = {}
    
    try:
        # エラーが発生する前にダミーチャートを準備
        dummy_chart = {
            "data": [{
                "x": [0, 1],
                "y": [0, 1],
                "mode": "lines",
                "type": "scatter",
                "showlegend": "false"  # JavaScriptに渡す用に文字列化
            }],
            "layout": {
                "height": 300,
                "title": {"text": "データがロードされていません"},
                "annotations": [{
                    "text": "データ準備中...",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": "false",  # JavaScriptに渡す用に文字列化
                    "font": {"size": 14, "color": "blue"}
                }]
            }
        }
        
        if dataset_name == "population":
            # 人口データの処理
            # 可視化1: 総人口の推移
            total_pop_by_year = df.groupby("年")["総人口"].sum().reset_index()
            year_values = total_pop_by_year["年"].tolist()
            pop_values = total_pop_by_year["総人口"].tolist()
            
            population_trend = {
                "data": [{
                    "x": year_values,
                    "y": pop_values,
                    "type": "scatter",
                    "mode": "lines+markers",
                    "name": "総人口",
                    "line": {"color": "royalblue", "width": 3},
                    "marker": {"size": 8}
                }],
                "layout": {
                    "title": {"text": "日本の総人口推移"},
                    "xaxis": {"title": "年"},
                    "yaxis": {"title": "人口"},
                    "hovermode": "closest",
                    "height": 450,
                    "template": "plotly_white"
                }
            }
            visualizations["total_population_trend"] = population_trend
            
            # 可視化2: 年齢層別人口構成比の推移
            age_groups = df.groupby("年")[["0-14歳", "15-64歳", "65歳以上"]].sum().reset_index()
            year_list = age_groups["年"].tolist()
            young_values = age_groups["0-14歳"].tolist()
            working_values = age_groups["15-64歳"].tolist()
            elderly_values = age_groups["65歳以上"].tolist()
            
            age_trend = {
                "data": [
                    {
                        "x": year_list,
                        "y": young_values,
                        "stackgroup": "one",
                        "name": "0-14歳",
                        "fillcolor": "#2E86C1"
                    },
                    {
                        "x": year_list,
                        "y": working_values,
                        "stackgroup": "one",
                        "name": "15-64歳",
                        "fillcolor": "#28B463"
                    },
                    {
                        "x": year_list,
                        "y": elderly_values,
                        "stackgroup": "one",
                        "name": "65歳以上",
                        "fillcolor": "#E67E22"
                    }
                ],
                "layout": {
                    "title": {"text": "年齢層別人口構成の推移"},
                    "xaxis": {"title": "年"},
                    "yaxis": {"title": "人口"},
                    "hovermode": "closest",
                    "template": "plotly_white",
                    "height": 450
                }
            }
            visualizations["age_group_trend"] = age_trend
            
            # 可視化3: 最新年の都道府県別人口
            latest_year = df["年"].max()
            latest_pop = df[df["年"] == latest_year][["都道府県", "総人口"]].sort_values("総人口", ascending=False)
            prefecture_list = latest_pop["都道府県"].tolist()
            population_list = latest_pop["総人口"].tolist()
            
            prefecture_population = {
                "data": [{
                    "x": prefecture_list,
                    "y": population_list,
                    "type": "bar",
                    "marker": {"color": "royalblue"}
                }],
                "layout": {
                    "title": {"text": f"{latest_year}年 都道府県別人口"},
                    "xaxis": {"title": "都道府県", "automargin": True},
                    "yaxis": {"title": "人口"},
                    "height": 450,
                    "template": "plotly_white"
                }
            }
            visualizations["prefecture_population"] = prefecture_population
            
        elif dataset_name == "weather":
            # 気象データの処理
            # 可視化1: 主要都市の年間平均気温推移
            major_cities = ["東京", "大阪", "札幌", "福岡", "那覇"]
            city_temp = df[df["都市"].isin(major_cities)].groupby(["年", "都市"])["平均気温(°C)"].mean().reset_index()
            
            # 各都市ごとのデータを作成
            city_traces = []
            for city in major_cities:
                city_data = city_temp[city_temp["都市"] == city]
                if not city_data.empty:
                    city_traces.append({
                        "x": city_data["年"].tolist(),
                        "y": city_data["平均気温(°C)"].tolist(),
                        "type": "scatter",
                        "mode": "lines+markers",
                        "name": city
                    })
            
            city_temp_trend = {
                "data": city_traces,
                "layout": {
                    "title": {"text": "主要都市の年間平均気温推移"},
                    "xaxis": {"title": "年"},
                    "yaxis": {"title": "平均気温(°C)"},
                    "hovermode": "closest",
                    "height": 450,
                    "template": "plotly_white"
                }
            }
            visualizations["city_temperature_trend"] = city_temp_trend
            
            # 可視化2: 月別平均気温の比較（最新年）
            latest_year = df["年"].max()
            monthly_temp = df[df["年"] == latest_year]
            monthly_temp["月番号"] = monthly_temp["月"].str.replace("月", "").astype(int)
            monthly_temp = monthly_temp.sort_values("月番号")
            
            # 各都市ごとのデータを作成
            monthly_traces = []
            for city in major_cities:
                city_data = monthly_temp[monthly_temp["都市"] == city]
                if not city_data.empty:
                    monthly_traces.append({
                        "x": city_data["月"].tolist(),
                        "y": city_data["平均気温(°C)"].tolist(),
                        "type": "scatter",
                        "mode": "lines+markers",
                        "name": city
                    })
            
            monthly_temp_chart = {
                "data": monthly_traces,
                "layout": {
                    "title": {"text": f"{latest_year}年 主要都市の月別平均気温"},
                    "xaxis": {"title": "月"},
                    "yaxis": {"title": "平均気温(°C)"},
                    "hovermode": "closest",
                    "height": 450,
                    "template": "plotly_white"
                }
            }
            visualizations["monthly_temperature"] = monthly_temp_chart
            
            # 可視化3: 都市別年間降水量（最新年）
            annual_precip = df[df["年"] == latest_year].groupby("都市")["降水量(mm)"].sum().reset_index().sort_values("降水量(mm)", ascending=False)
            cities = annual_precip["都市"].tolist()
            precip = annual_precip["降水量(mm)"].tolist()
            
            city_precip = {
                "data": [{
                    "x": cities,
                    "y": precip,
                    "type": "bar",
                    "marker": {"color": "steelblue"}
                }],
                "layout": {
                    "title": {"text": f"{latest_year}年 都市別年間降水量"},
                    "xaxis": {"title": "都市", "automargin": True},
                    "yaxis": {"title": "降水量(mm)"},
                    "height": 450,
                    "template": "plotly_white"
                }
            }
            visualizations["city_precipitation"] = city_precip
            
        elif dataset_name == "energy":
            # エネルギーデータの処理
            # 可視化1: エネルギー源別発電量の推移
            # 各年とエネルギー源ごとのデータをピボットで作成
            energy_pivot = df.pivot_table(
                index="年", 
                columns="エネルギー源", 
                values="発電量(TWh)"
            ).reset_index()
            
            # エネルギー源のリスト取得
            energy_sources = df["エネルギー源"].unique().tolist()
            years = energy_pivot["年"].tolist()
            
            # 各エネルギー源のトレースを作成
            energy_traces = []
            for source in energy_sources:
                if source in energy_pivot.columns:
                    energy_traces.append({
                        "x": years,
                        "y": energy_pivot[source].tolist(),
                        "type": "scatter",
                        "mode": "lines",
                        "stackgroup": "one",
                        "name": source
                    })
            
            energy_trend = {
                "data": energy_traces,
                "layout": {
                    "title": {"text": "日本のエネルギー源別発電量推移"},
                    "xaxis": {"title": "年"},
                    "yaxis": {"title": "発電量(TWh)"},
                    "hovermode": "closest",
                    "height": 450,
                    "template": "plotly_white"
                }
            }
            visualizations["energy_source_trend"] = energy_trend
            
            # 可視化2: 最新年のエネルギー構成
            latest_year = df["年"].max()
            latest_energy = df[df["年"] == latest_year]
            sources = latest_energy["エネルギー源"].tolist()
            values = latest_energy["発電量(TWh)"].tolist()
            
            energy_pie = {
                "data": [{
                    "values": values,
                    "labels": sources,
                    "type": "pie",
                    "textinfo": "label+percent",
                    "hoverinfo": "label+value+percent"
                }],
                "layout": {
                    "title": {"text": f"{latest_year}年 日本のエネルギー構成"},
                    "height": 450,
                    "template": "plotly_white"
                }
            }
            visualizations["energy_composition"] = energy_pie
            
            # 可視化3: 再生可能エネルギーの成長
            renewable = df[df["エネルギー源"].isin(["水力", "太陽光", "風力", "バイオマス"])]
            renewable_pivot = renewable.pivot_table(
                index="年", 
                columns="エネルギー源", 
                values="発電量(TWh)"
            ).reset_index()
            
            renewable_sources = ["水力", "太陽光", "風力", "バイオマス"]
            renewable_years = renewable_pivot["年"].tolist()
            
            renewable_traces = []
            for source in renewable_sources:
                if source in renewable_pivot.columns:
                    renewable_traces.append({
                        "x": renewable_years,
                        "y": renewable_pivot[source].tolist(),
                        "type": "scatter",
                        "mode": "lines+markers",
                        "name": source
                    })
            
            renewable_chart = {
                "data": renewable_traces,
                "layout": {
                    "title": {"text": "再生可能エネルギー源の発電量推移"},
                    "xaxis": {"title": "年"},
                    "yaxis": {"title": "発電量(TWh)"},
                    "hovermode": "closest",
                    "height": 450,
                    "template": "plotly_white"
                }
            }
            visualizations["renewable_energy_growth"] = renewable_chart
            
        elif dataset_name == "transport":
            # 交通データの処理
            # 可視化1: 交通手段別輸送人員の推移
            transport_by_year = df.groupby(["年", "交通手段"])["輸送人員(百万人)"].sum().reset_index()
            
            # 交通手段のリスト取得
            transport_modes = df["交通手段"].unique().tolist()
            
            # 各交通手段のトレースを作成
            transport_traces = []
            for mode in transport_modes:
                mode_data = transport_by_year[transport_by_year["交通手段"] == mode]
                transport_traces.append({
                    "x": mode_data["年"].tolist(),
                    "y": mode_data["輸送人員(百万人)"].tolist(),
                    "type": "scatter",
                    "mode": "lines+markers",
                    "name": mode
                })
            
            transport_trend = {
                "data": transport_traces,
                "layout": {
                    "title": {"text": "交通手段別輸送人員の推移"},
                    "xaxis": {"title": "年"},
                    "yaxis": {"title": "輸送人員(百万人)"},
                    "hovermode": "closest",
                    "height": 450,
                    "template": "plotly_white"
                }
            }
            visualizations["transport_mode_trend"] = transport_trend
            
            # 可視化2: 地域別交通手段構成（最新年）
            latest_year = df["年"].max()
            latest_transport = df[df["年"] == latest_year]
            
            # 地域と交通手段でグループ化
            region_transport = latest_transport.groupby(["地域", "交通手段"])["輸送人員(百万人)"].sum().reset_index()
            
            # 地域ごとに積み上げ棒グラフを作成
            regions = df["地域"].unique().tolist()
            regional_transport_data = []
            
            for mode in transport_modes:
                mode_data = region_transport[region_transport["交通手段"] == mode]
                if not mode_data.empty:
                    regional_transport_data.append({
                        "x": mode_data["地域"].tolist(),
                        "y": mode_data["輸送人員(百万人)"].tolist(),
                        "type": "bar",
                        "name": mode
                    })
            
            regional_chart = {
                "data": regional_transport_data,
                "layout": {
                    "title": {"text": f"{latest_year}年 地域別交通手段構成"},
                    "xaxis": {"title": "地域"},
                    "yaxis": {"title": "輸送人員(百万人)"},
                    "barmode": "stack",
                    "height": 450,
                    "template": "plotly_white"
                }
            }
            visualizations["regional_transport_composition"] = regional_chart
            
            # 可視化3: 公共交通機関の地域別比較（最新年）
            public_transport = latest_transport[
                latest_transport["交通手段"].isin(["鉄道", "バス", "タクシー", "航空", "船舶"])
            ]
            
            # 地域と交通手段でグループ化
            public_region_transport = public_transport.groupby(["地域", "交通手段"])["輸送人員(百万人)"].sum().reset_index()
            
            # 地域ごとに積み上げ棒グラフを作成
            public_modes = ["鉄道", "バス", "タクシー", "航空", "船舶"]
            public_transport_data = []
            
            for mode in public_modes:
                mode_data = public_region_transport[public_region_transport["交通手段"] == mode]
                if not mode_data.empty:
                    public_transport_data.append({
                        "x": mode_data["地域"].tolist(),
                        "y": mode_data["輸送人員(百万人)"].tolist(),
                        "type": "bar",
                        "name": mode
                    })
            
            public_chart = {
                "data": public_transport_data,
                "layout": {
                    "title": {"text": f"{latest_year}年 地域別公共交通機関利用"},
                    "xaxis": {"title": "地域"},
                    "yaxis": {"title": "輸送人員(百万人)"},
                    "barmode": "stack",
                    "height": 450,
                    "template": "plotly_white"
                }
            }
            visualizations["regional_public_transport"] = public_chart
            
    except Exception as e:
        print(f"Error creating visualizations: {str(e)}")
        
        # エラー表示用のチャート
        error_chart = {
            "data": [{
                "x": [0, 1],
                "y": [0, 1],
                "mode": "lines",
                "type": "scatter",
                "showlegend": "false"  # JavaScriptに渡す用に文字列化
            }],
            "layout": {
                "height": 300,
                "annotations": [{
                    "text": f"データ可視化エラー: {str(e)}",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": "false",  # JavaScriptに渡す用に文字列化
                    "font": {"size": 14, "color": "red"}
                }]
            }
        }
        
        # 全データセットタイプに対するエラービジュアライゼーション
        if dataset_name == "population":
            visualizations = {
                "total_population_trend": error_chart,
                "age_group_trend": error_chart,
                "prefecture_population": error_chart
            }
        elif dataset_name == "weather":
            visualizations = {
                "city_temperature_trend": error_chart,
                "monthly_temperature": error_chart,
                "city_precipitation": error_chart
            }
        elif dataset_name == "energy":
            visualizations = {
                "energy_source_trend": error_chart,
                "energy_composition": error_chart,
                "renewable_energy_growth": error_chart
            }
        elif dataset_name == "transport":
            visualizations = {
                "transport_mode_trend": error_chart,
                "regional_transport_composition": error_chart,
                "regional_public_transport": error_chart
            }
        else:
            visualizations = {"error": str(e)}
    
    # 全てのブール値を文字列化してからJSONに変換することで
    # JavaScriptと互換性を持たせる
    visualizations = convert_booleans_to_js(visualizations)
    return visualizations