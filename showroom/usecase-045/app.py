import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import openai
import markdown

# Handle Markup compatibility between Flask 2.x and 3.x
try:
    from flask import Markup
except ImportError:
    from markupsafe import Markup

# 環境変数の読み込み
load_dotenv()

# ユーティリティモジュールのインポート
from utils.data_generators import initialize_datasets, load_dataset
from utils.data_analysis import analyze_data
from utils.visualization import create_visualizations

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key")

# OpenAIクライアントの初期化
client = openai.Client(api_key=os.environ.get("OPENAI_API_KEY"))


@app.route("/")
def index():
    # データセットの初期化（存在しない場合）
    if not os.path.exists("showroom/usecase-045/static/data"):
        initialize_datasets()

    return render_template("index.html")


@app.route("/dataset/<dataset_name>", methods=["GET", "POST"])
def dataset_view(dataset_name):
    specific_query = None
    if request.method == "POST":
        specific_query = request.form.get("query", "")

    # データの読み込み
    df = load_dataset(dataset_name)

    # データ分析
    stats, explanations = analyze_data(dataset_name, client, specific_query)

    # マークダウンをHTMLに変換
    html_content = markdown.markdown(explanations)
    explanations = Markup(html_content)

    # 可視化の作成
    visualizations = create_visualizations(dataset_name, df)

    friendly_names = {
        "population": "人口統計データ",
        "weather": "気象データ",
        "energy": "エネルギーデータ",
        "transport": "交通データ",
    }

    return render_template(
        "dataset.html",
        dataset_name=dataset_name,
        friendly_name=friendly_names.get(dataset_name, dataset_name),
        stats=stats,
        explanations=explanations,
        visualizations=visualizations,
        query=specific_query,
    )


@app.route("/api/datasets")
def api_datasets():
    available_datasets = ["population", "weather", "energy", "transport"]
    datasets_info = {
        "population": {
            "name": "人口統計データ",
            "description": "日本の都道府県別人口データ（年齢層別）",
            "period": "2010-2022年",
            "icon": "fa-users",
        },
        "weather": {
            "name": "気象データ",
            "description": "日本の主要都市の気温・降水量データ",
            "period": "2018-2022年",
            "icon": "fa-cloud-sun-rain",
        },
        "energy": {
            "name": "エネルギーデータ",
            "description": "日本のエネルギー源別発電量データ",
            "period": "2010-2022年",
            "icon": "fa-bolt",
        },
        "transport": {
            "name": "交通データ",
            "description": "日本の地域別・交通手段別輸送人員データ",
            "period": "2010-2022年",
            "icon": "fa-train",
        },
    }

    return jsonify(datasets_info)


if __name__ == "__main__":
    # データセットの初期化
    initialize_datasets()
    app.run(debug=True, port=5020)
