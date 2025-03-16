"""
データ分析レポート自動生成: 販売データからOpenAI APIを使用して分析レポートを自動生成
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.io as pio
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import base64
import json
from jinja2 import Environment, FileSystemLoader
import io
import matplotlib
matplotlib.use('Agg')

# .envファイルから環境変数を読み込む
load_dotenv()

# OpenAI APIクライアントを初期化
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# データの読み込み
def load_data():
    """販売データを読み込む"""
    csv_path = os.path.join(os.path.dirname(__file__), "data", "sales_data.csv")
    df = pd.read_csv(csv_path)
    # 日付列を日付型に変換
    df['Date'] = pd.to_datetime(df['Date'])
    return df

# 基本的な統計情報を生成
def generate_basic_stats(df):
    """基本的な統計情報を生成する"""
    stats = {
        "total_sales": df['Sales'].sum(),
        "total_units": df['Units'].sum(),
        "avg_price": df['Price'].mean(),
        "sales_by_category": df.groupby('Category')['Sales'].sum().to_dict(),
        "sales_by_region": df.groupby('Region')['Sales'].sum().to_dict(),
        "sales_by_product": df.groupby('Product')['Sales'].sum().to_dict(),
        "monthly_sales": df.groupby(df['Date'].dt.strftime('%Y-%m'))['Sales'].sum().to_dict()
    }
    return stats

# プロモーション効果の分析
def analyze_promotion_effect(df):
    """プロモーションの効果を分析する"""
    promo_effect = df.groupby('Promotion')['Sales'].agg(['mean', 'sum', 'count']).reset_index()
    promo_effect.columns = ['Promotion', 'Average_Sales', 'Total_Sales', 'Count']
    
    # プロモーション別の平均販売数
    promo_units = df.groupby('Promotion')['Units'].mean().reset_index()
    promo_units.columns = ['Promotion', 'Average_Units']
    
    promo_effect = pd.merge(promo_effect, promo_units, on='Promotion')
    return promo_effect

# グラフ生成関数
def create_visualizations(df):
    """データ可視化グラフを生成する"""
    # 保存用のディレクトリを作成
    image_dir = os.path.join(os.path.dirname(__file__), "images")
    os.makedirs(image_dir, exist_ok=True)
    
    # Base64エンコードされた画像URLと説明のリスト
    visualizations = []
    
    # 1. 月別売上推移
    plt.figure(figsize=(12, 6))
    monthly_sales = df.groupby(df['Date'].dt.strftime('%Y-%m'))['Sales'].sum()
    monthly_sales.index = pd.to_datetime(monthly_sales.index + '-01')
    plt.plot(monthly_sales.index, monthly_sales.values, marker='o', linestyle='-')
    plt.title('Monthly Sales Trend')
    plt.xlabel('Month')
    plt.ylabel('Sales')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # 画像をBase64エンコード
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
    visualizations.append({
        "title": "Monthly Sales Trend",
        "image_data": f"data:image/png;base64,{img_base64}",
        "description": "2023年の月別売上推移"
    })
    plt.close()
    
    # 2. カテゴリ別売上
    plt.figure(figsize=(10, 6))
    category_sales = df.groupby('Category')['Sales'].sum().sort_values(ascending=False)
    sns.barplot(x=category_sales.index, y=category_sales.values)
    plt.title('Sales by Category')
    plt.xlabel('Category')
    plt.ylabel('Sales')
    plt.xticks(rotation=0)
    plt.tight_layout()
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
    visualizations.append({
        "title": "Sales by Category",
        "image_data": f"data:image/png;base64,{img_base64}",
        "description": "カテゴリ別の売上合計"
    })
    plt.close()
    
    # 3. 地域別売上
    plt.figure(figsize=(10, 6))
    region_sales = df.groupby('Region')['Sales'].sum().sort_values(ascending=False)
    sns.barplot(x=region_sales.index, y=region_sales.values)
    plt.title('Sales by Region')
    plt.xlabel('Region')
    plt.ylabel('Sales')
    plt.tight_layout()
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
    visualizations.append({
        "title": "Sales by Region",
        "image_data": f"data:image/png;base64,{img_base64}",
        "description": "地域別の売上合計"
    })
    plt.close()
    
    # 4. 製品別売上
    plt.figure(figsize=(12, 6))
    product_sales = df.groupby('Product')['Sales'].sum().sort_values(ascending=False)
    sns.barplot(x=product_sales.index, y=product_sales.values)
    plt.title('Sales by Product')
    plt.xlabel('Product')
    plt.ylabel('Sales')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
    visualizations.append({
        "title": "Sales by Product",
        "image_data": f"data:image/png;base64,{img_base64}",
        "description": "製品別の売上合計"
    })
    plt.close()
    
    # 5. プロモーション効果の比較
    plt.figure(figsize=(10, 6))
    promo_effect = df.groupby('Promotion')['Sales'].mean().reset_index()
    sns.barplot(x='Promotion', y='Sales', data=promo_effect)
    plt.title('Average Sales by Promotion Status')
    plt.xlabel('Promotion Applied')
    plt.ylabel('Average Sales')
    plt.tight_layout()
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
    visualizations.append({
        "title": "Average Sales by Promotion Status",
        "image_data": f"data:image/png;base64,{img_base64}",
        "description": "プロモーション有無による平均売上の比較"
    })
    plt.close()
    
    return visualizations

# OpenAI APIを使用して分析レポートを生成
def generate_report_with_openai(data, stats, promo_effect, visualizations):
    """OpenAI APIを使用して分析レポートを生成する"""
    
    # 前処理されたデータから必要な情報を抽出
    categories = data['Category'].unique().tolist()
    regions = data['Region'].unique().tolist()
    products = data['Product'].unique().tolist()
    
    # 統計情報をわかりやすい形式に整形
    formatted_stats = {
        "総売上": f"¥{stats['total_sales']:,.0f}",
        "総販売数": f"{stats['total_units']:,.0f}個",
        "平均価格": f"¥{stats['avg_price']:,.0f}",
        "カテゴリ別売上": {k: f"¥{v:,.0f}" for k, v in stats['sales_by_category'].items()},
        "地域別売上": {k: f"¥{v:,.0f}" for k, v in stats['sales_by_region'].items()},
        "製品別売上": {k: f"¥{v:,.0f}" for k, v in stats['sales_by_product'].items()},
    }
    
    # プロモーション効果の分析結果
    promotion_analysis = {
        "プロモーションあり": {
            "平均売上": f"¥{promo_effect[promo_effect['Promotion'] == 'Yes']['Average_Sales'].values[0]:,.0f}",
            "平均販売数": f"{promo_effect[promo_effect['Promotion'] == 'Yes']['Average_Units'].values[0]:,.1f}個"
        },
        "プロモーションなし": {
            "平均売上": f"¥{promo_effect[promo_effect['Promotion'] == 'No']['Average_Sales'].values[0]:,.0f}",
            "平均販売数": f"{promo_effect[promo_effect['Promotion'] == 'No']['Average_Units'].values[0]:,.1f}個"
        }
    }
    
    # 売上成長率の計算
    monthly_sales = pd.Series(stats['monthly_sales'])
    monthly_sales.index = pd.to_datetime(monthly_sales.index + '-01')
    monthly_sales = monthly_sales.sort_index()
    first_month_sales = monthly_sales.iloc[0]
    last_month_sales = monthly_sales.iloc[-1]
    growth_rate = ((last_month_sales / first_month_sales) - 1) * 100
    
    # 売上上位製品
    top_products = pd.Series(stats['sales_by_product']).sort_values(ascending=False).head(3).index.tolist()
    
    # OpenAI APIにリクエストするプロンプト
    prompt = f"""
    あなたは、販売データの専門的なデータアナリストです。以下の情報を元に、データを分析し、ビジネス上の洞察を提供してください。
    レポートは日本語で作成し、マークダウン形式で出力してください。

    # 基本情報
    - 対象期間: 2023年1月から12月
    - 総売上: {formatted_stats['総売上']}
    - 総販売数: {formatted_stats['総販売数']}
    - 平均価格: {formatted_stats['平均価格']}
    - 売上成長率: {growth_rate:.1f}%（1月から12月）
    
    # カテゴリ情報
    {json.dumps(formatted_stats['カテゴリ別売上'], indent=2, ensure_ascii=False)}
    
    # 地域情報
    {json.dumps(formatted_stats['地域別売上'], indent=2, ensure_ascii=False)}
    
    # 製品情報
    - 売上上位製品: {', '.join(top_products)}
    
    # プロモーション効果
    {json.dumps(promotion_analysis, indent=2, ensure_ascii=False)}
    
    以下のセクションを含むレポートを作成してください:
    
    1. エグゼクティブサマリー
    2. 売上分析
       - トレンド分析
       - カテゴリ別分析
       - 地域別分析
       - 製品別分析
    3. プロモーション効果分析
    4. 分析から得られる洞察
    5. 次四半期に向けての提案
    
    ビジネス用語を適切に使用し、経営者が意思決定に活用できる具体的な洞察と行動提案を含めてください。
    """
    
    # OpenAI APIを呼び出し
    print("OpenAI APIを呼び出してレポートを生成中...")
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "あなたは、販売データ分析の専門家です。データから実用的なビジネス洞察を提供します。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    report_content = response.choices[0].message.content
    return report_content

# HTMLレポートの生成
def generate_html_report(report_content, visualizations):
    """HTMLレポートを生成する"""
    # Jinja2テンプレート環境を設定
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    os.makedirs(template_dir, exist_ok=True)
    
    # HTMLテンプレートを作成
    template_path = os.path.join(template_dir, "report_template.html")
    with open(template_path, "w", encoding="utf-8") as f:
        f.write("""
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>販売データ分析レポート</title>
            <style>
                body {
                    font-family: 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                h1 {
                    color: #2c3e50;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 10px;
                }
                h2 {
                    color: #2980b9;
                    margin-top: 30px;
                }
                h3 {
                    color: #3498db;
                }
                .report-date {
                    color: #7f8c8d;
                    font-size: 0.9em;
                    margin-bottom: 30px;
                }
                .visualization {
                    margin: 30px 0;
                    text-align: center;
                }
                .visualization img {
                    max-width: 100%;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    border-radius: 5px;
                }
                .visualization-title {
                    font-weight: bold;
                    margin-top: 10px;
                    font-size: 1.1em;
                }
                .visualization-description {
                    color: #555;
                    font-size: 0.9em;
                }
                .report-content {
                    margin-top: 40px;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }
                th, td {
                    padding: 10px;
                    border: 1px solid #ddd;
                }
                th {
                    background-color: #f6f8fa;
                }
                tr:nth-child(even) {
                    background-color: #f9f9f9;
                }
            </style>
        </head>
        <body>
            <h1>販売データ分析レポート</h1>
            <div class="report-date">
                レポート生成日: {{ generation_date }}
            </div>
            
            <div class="visualizations">
                {% for viz in visualizations %}
                <div class="visualization">
                    <img src="{{ viz.image_data }}" alt="{{ viz.title }}">
                    <div class="visualization-title">{{ viz.title }}</div>
                    <div class="visualization-description">{{ viz.description }}</div>
                </div>
                {% endfor %}
            </div>
            
            <div class="report-content">
                {{ report_content | safe }}
            </div>
        </body>
        </html>
        """)
    
    # テンプレート環境を作成
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("report_template.html")
    
    # マークダウンをHTMLに変換（簡易的な変換）
    lines = report_content.split('\n')
    html_content = []
    in_list = False
    
    for line in lines:
        if line.startswith('# '):
            html_content.append(f'<h2>{line[2:]}</h2>')
        elif line.startswith('## '):
            html_content.append(f'<h3>{line[3:]}</h3>')
        elif line.startswith('### '):
            html_content.append(f'<h4>{line[4:]}</h4>')
        elif line.startswith('- '):
            if not in_list:
                html_content.append('<ul>')
                in_list = True
            html_content.append(f'<li>{line[2:]}</li>')
        elif line.startswith('1. ') or line.startswith('2. ') or line.startswith('3. '):
            parts = line.split('. ', 1)
            if len(parts) > 1:
                html_content.append(f'<p><strong>{parts[0]}.</strong> {parts[1]}</p>')
            else:
                html_content.append(f'<p>{line}</p>')
        elif line.strip() == '':
            if in_list:
                html_content.append('</ul>')
                in_list = False
            html_content.append('<p></p>')
        else:
            if in_list:
                html_content.append('</ul>')
                in_list = False
            html_content.append(f'<p>{line}</p>')
    
    if in_list:
        html_content.append('</ul>')
    
    html_report_content = '\n'.join(html_content)
    
    # レポートに今日の日付を追加
    today = datetime.now().strftime('%Y年%m月%d日')
    
    # HTMLレポートを生成
    html_report = template.render(
        report_content=html_report_content,
        visualizations=visualizations,
        generation_date=today
    )
    
    # HTMLファイルとして保存
    report_path = os.path.join(os.path.dirname(__file__), "report.html")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_report)
    
    return report_path

def main():
    """メイン関数"""
    try:
        print("データ分析レポート自動生成を開始します...")
        
        # データの読み込み
        print("データを読み込んでいます...")
        df = load_data()
        print(f"読み込み完了: {len(df)}行のデータを取得")
        
        # 基本統計情報の生成
        print("基本統計情報を生成しています...")
        stats = generate_basic_stats(df)
        
        # プロモーション効果の分析
        print("プロモーション効果を分析しています...")
        promo_effect = analyze_promotion_effect(df)
        
        # データ可視化の生成
        print("データ可視化を生成しています...")
        visualizations = create_visualizations(df)
        
        # レポートの生成
        print("分析レポートを生成しています...")
        report_content = generate_report_with_openai(df, stats, promo_effect, visualizations)
        
        # HTMLレポートの生成
        print("HTMLレポートを生成しています...")
        report_path = generate_html_report(report_content, visualizations)
        
        print(f"レポート生成完了！レポートは {report_path} に保存されました。")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()