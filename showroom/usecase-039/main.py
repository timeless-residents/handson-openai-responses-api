#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
usecase-039: データ分析と可視化レポート生成

Responses APIを使用してデータ分析とインサイト抽出を行い、
対話的なレポートを生成するサンプルコード。
"""

import os
import json
import argparse
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import openai
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress
from jinja2 import Environment, FileSystemLoader

# 環境変数の読み込み
dotenv_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path)

# APIキーの設定
openai.api_key = os.getenv("OPENAI_API_KEY")

# コンソール設定
console = Console()

# 定数
DEFAULT_DATA_FILE = Path(__file__).parent / "sample_data.csv"
REPORTS_DIR = Path(__file__).parent / "reports"
CHARTS_DIR = Path(__file__).parent / "charts"

# ディレクトリが存在しない場合は作成
REPORTS_DIR.mkdir(exist_ok=True)
CHARTS_DIR.mkdir(exist_ok=True)

def load_data(file_path: str) -> Tuple[pd.DataFrame, str]:
    """データファイルを読み込む"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
    
    # ファイル拡張子に基づいて読み込み方法を選択
    if file_path.suffix.lower() == '.csv':
        df = pd.read_csv(file_path)
        data_format = 'csv'
    elif file_path.suffix.lower() in ['.json', '.jsonl']:
        df = pd.read_json(file_path)
        data_format = 'json'
    elif file_path.suffix.lower() in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
        data_format = 'excel'
    else:
        raise ValueError(f"サポートされていないファイル形式です: {file_path.suffix}")
    
    return df, data_format

def generate_summary_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """データフレームの要約統計量を生成"""
    summary = {}
    
    # 基本情報
    summary['row_count'] = len(df)
    summary['column_count'] = len(df.columns)
    summary['columns'] = df.columns.tolist()
    
    # 数値列の統計量
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_columns:
        summary['numeric_stats'] = {}
        for col in numeric_columns:
            summary['numeric_stats'][col] = {
                'mean': df[col].mean(),
                'median': df[col].median(),
                'std': df[col].std(),
                'min': df[col].min(),
                'max': df[col].max()
            }
    
    # カテゴリ列の統計量
    categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
    if categorical_columns:
        summary['categorical_stats'] = {}
        for col in categorical_columns:
            value_counts = df[col].value_counts().to_dict()
            summary['categorical_stats'][col] = {
                'unique_count': df[col].nunique(),
                'top_values': dict(sorted(value_counts.items(), key=lambda x: x[1], reverse=True)[:5])
            }
    
    # 日付列の検出と統計量
    date_columns = []
    for col in df.columns:
        try:
            if df[col].dtype == 'object':
                # 日付への変換を試みる
                pd.to_datetime(df[col])
                date_columns.append(col)
        except:
            continue
    
    if date_columns:
        summary['date_stats'] = {}
        for col in date_columns:
            dates = pd.to_datetime(df[col])
            summary['date_stats'][col] = {
                'min_date': dates.min().isoformat(),
                'max_date': dates.max().isoformat(),
                'range_days': (dates.max() - dates.min()).days
            }
    
    return summary

def create_visualization_charts(df: pd.DataFrame) -> List[Dict[str, str]]:
    """データの可視化チャートを作成"""
    charts = []
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 数値列の検出
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # カテゴリ列の検出
    categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
    
    # 1. カテゴリ列の分布図（上位5カテゴリ）
    if categorical_columns:
        for i, col in enumerate(categorical_columns[:2]):  # 最初の2つのカテゴリ列のみ処理
            plt.figure(figsize=(10, 6))
            top_categories = df[col].value_counts().nlargest(5)
            top_categories.plot(kind='bar', color='skyblue')
            plt.title(f'{col}の分布 (上位5)')
            plt.xlabel(col)
            plt.ylabel('頻度')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            chart_path = CHARTS_DIR / f"category_dist_{i}_{timestamp}.png"
            plt.savefig(chart_path)
            plt.close()
            
            charts.append({
                "title": f"{col}の分布",
                "path": str(chart_path)
            })
    
    # 2. 数値データの箱ひげ図
    if len(numeric_columns) > 0:
        plt.figure(figsize=(12, 6))
        df[numeric_columns].plot(kind='box', vert=False)
        plt.title('数値データの分布')
        plt.tight_layout()
        
        chart_path = CHARTS_DIR / f"boxplot_{timestamp}.png"
        plt.savefig(chart_path)
        plt.close()
        
        charts.append({
            "title": "数値データの分布（箱ひげ図）",
            "path": str(chart_path)
        })
    
    # 3. 数値列間の相関ヒートマップ
    if len(numeric_columns) > 1:
        plt.figure(figsize=(10, 8))
        correlation = df[numeric_columns].corr()
        plt.imshow(correlation, cmap='coolwarm', interpolation='none', aspect='auto')
        plt.colorbar()
        plt.xticks(range(len(correlation.columns)), correlation.columns, rotation=90)
        plt.yticks(range(len(correlation.columns)), correlation.columns)
        plt.title('相関ヒートマップ')
        
        # 相関係数をプロット
        for i in range(len(correlation.columns)):
            for j in range(len(correlation.columns)):
                plt.text(j, i, f'{correlation.iloc[i, j]:.2f}',
                        ha='center', va='center', color='white' if abs(correlation.iloc[i, j]) > 0.5 else 'black')
        
        plt.tight_layout()
        
        chart_path = CHARTS_DIR / f"correlation_{timestamp}.png"
        plt.savefig(chart_path)
        plt.close()
        
        charts.append({
            "title": "変数間の相関ヒートマップ",
            "path": str(chart_path)
        })
    
    # 4. 時系列データがあれば時系列プロット
    date_columns = []
    for col in df.columns:
        try:
            if df[col].dtype == 'object':
                pd.to_datetime(df[col])
                date_columns.append(col)
        except:
            continue
    
    if date_columns and numeric_columns:
        date_col = date_columns[0]  # 最初の日付列を使用
        numeric_col = numeric_columns[0]  # 最初の数値列を使用
        
        plt.figure(figsize=(12, 6))
        
        # 日付データへの変換と並べ替え
        df_sorted = df.copy()
        df_sorted[date_col] = pd.to_datetime(df_sorted[date_col])
        df_sorted = df_sorted.sort_values(by=date_col)
        
        # 時系列プロット
        plt.plot(df_sorted[date_col], df_sorted[numeric_col], marker='o', linestyle='-', color='blue')
        plt.title(f'{numeric_col}の時系列変化')
        plt.xlabel(date_col)
        plt.ylabel(numeric_col)
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        chart_path = CHARTS_DIR / f"time_series_{timestamp}.png"
        plt.savefig(chart_path)
        plt.close()
        
        charts.append({
            "title": f"{numeric_col}の時系列変化",
            "path": str(chart_path)
        })
        
    return charts

def create_analysis_request(df: pd.DataFrame, stats: Dict[str, Any], charts: List[Dict[str, str]]) -> Dict[str, Any]:
    """分析リクエストを作成"""
    # データサンプルの準備
    data_sample = df.head(10).to_dict()
    
    # チャートの説明
    chart_descriptions = []
    for chart in charts:
        chart_descriptions.append(f"- {chart['title']}")
    
    # リクエストの作成
    return {
        "model": "gpt-4o",
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": """あなたは専門的なデータアナリストです。提供されたデータと統計情報を分析し、ビジネス価値のあるインサイトを抽出してください。

あなたの分析は以下のJSON形式で返してください:
{
  "summary": "データセットの全体概要と主な特徴をまとめた1-2段落のテキスト",
  "key_metrics": {
    "metric1": "値と簡単な説明",
    "metric2": "値と簡単な説明",
    "...": "..."
  },
  "insights": [
    "主要な発見1",
    "主要な発見2",
    "...",
    "主要な発見5"
  ],
  "trends": [
    "検出された傾向1",
    "検出された傾向2",
    "...",
    "検出された傾向5"
  ],
  "recommendations": [
    "ビジネスに活かせる推奨アクション1",
    "ビジネスに活かせる推奨アクション2",
    "...",
    "ビジネスに活かせる推奨アクション5"
  ]
}

- ビジネスに役立つ実用的なインサイトを提供してください
- 専門用語を避け、明確かつ簡潔に表現してください
- データから証拠に基づいた洞察を導き出してください
- 単なる統計の繰り返しではなく、意味のある解釈を心がけてください"""
            },
            {
                "role": "user",
                "content": f"""以下のデータセットを分析し、ビジネスインサイトを提供してください。

データサンプル:
{json.dumps(data_sample, indent=2, ensure_ascii=False)}

統計概要:
{json.dumps(stats, indent=2, ensure_ascii=False)}

作成された可視化:
{"".join(chart_descriptions)}

このデータを分析し、ビジネスに役立つインサイトと推奨事項を含む構造化されたレポートを生成してください。"""
            }
        ]
    }

def analyze_data(df: pd.DataFrame, charts: List[Dict[str, str]]) -> Dict[str, Any]:
    """データを分析してインサイトを抽出"""
    try:
        with Progress() as progress:
            # 進捗表示
            task1 = progress.add_task("[cyan]統計情報を計算中...", total=1)
            stats = generate_summary_statistics(df)
            progress.update(task1, completed=1)
            
            task2 = progress.add_task("[green]OpenAI APIでデータを分析中...", total=1)
            
            # OpenAI APIにリクエスト送信
            request = create_analysis_request(df, stats, charts)
            response = openai.chat.completions.create(**request)
            
            # JSONレスポンスを解析
            result = json.loads(response.choices[0].message.content)
            progress.update(task2, completed=1)
            
            return result
    
    except Exception as e:
        console.print(f"[bold red]エラーが発生しました: {e}[/bold red]")
        return {
            "summary": f"分析中にエラーが発生しました: {str(e)}",
            "key_metrics": {"エラー": "APIリクエストに失敗しました"},
            "insights": ["エラーのため分析結果を提供できません"],
            "trends": ["エラーのため傾向分析を提供できません"],
            "recommendations": ["システム管理者に連絡してください"]
        }

def generate_html_report(analysis: Dict[str, Any], charts: List[Dict[str, str]], output_path: Optional[Path] = None) -> str:
    """HTML形式の分析レポートを生成"""
    # テンプレート環境のセットアップ
    env = Environment(loader=FileSystemLoader(Path(__file__).parent / "templates"))
    template = env.get_template("report_template.html")
    
    # 現在の日時
    now = datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
    
    # テンプレートのレンダリング
    html_content = template.render(
        analysis=analysis,
        charts=charts,
        generation_time=now
    )
    
    # 出力ファイル名
    if output_path is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = REPORTS_DIR / f"data_analysis_report_{timestamp}.html"
    
    # HTMLファイルの書き込み
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return str(output_path)

def display_analysis_result(analysis: Dict[str, Any]) -> None:
    """分析結果をコンソールに表示"""
    # レポートヘッダーの表示
    console.print(Panel(
        "[bold]データ分析サマリー[/bold]\n\n" + analysis["summary"],
        title="分析結果",
        border_style="blue"
    ))
    
    # 主要指標の表示
    console.print("\n[bold cyan]主要指標:[/bold cyan]")
    for key, value in analysis["key_metrics"].items():
        console.print(f"[bold]{key}:[/bold] {value}")
    
    # インサイトの表示
    console.print("\n[bold green]主な発見:[/bold green]")
    for i, insight in enumerate(analysis["insights"], 1):
        console.print(f"{i}. {insight}")
    
    # 傾向の表示
    console.print("\n[bold yellow]検出された傾向:[/bold yellow]")
    for i, trend in enumerate(analysis["trends"], 1):
        console.print(f"{i}. {trend}")
    
    # 推奨事項の表示
    console.print("\n[bold magenta]推奨アクション:[/bold magenta]")
    for i, recommendation in enumerate(analysis["recommendations"], 1):
        console.print(f"{i}. {recommendation}")

def interactive_analysis(df: pd.DataFrame) -> None:
    """対話型の分析セッション"""
    console.print("\n[bold]データに対して質問できます (終了するには 'exit' と入力):[/bold]")
    
    while True:
        question = console.input("\n>> ")
        
        if question.lower() == 'exit':
            break
            
        with console.status("[bold green]質問を分析中...[/bold green]"):
            try:
                # OpenAI APIにリクエスト送信
                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "あなたはデータアナリストアシスタントです。ユーザーのデータに関する質問に具体的に答えてください。"
                        },
                        {
                            "role": "user",
                            "content": f"""以下のデータについて質問します：

データサンプル:
{df.head(10).to_markdown()}

質問: {question}

データの概要:
{df.describe().to_markdown()}
"""
                        }
                    ]
                )
                
                # 回答の表示
                answer = response.choices[0].message.content
                console.print(Panel(answer, title="回答", border_style="green"))
            
            except Exception as e:
                console.print(f"[bold red]エラーが発生しました: {e}[/bold red]")

def main() -> None:
    """メイン関数"""
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description="データ分析と可視化レポート生成")
    parser.add_argument("--file", type=str, default=str(DEFAULT_DATA_FILE),
                      help="分析するデータファイルのパス（CSV、JSON、Excelファイルをサポート）")
    args = parser.parse_args()
    
    # アプリケーションヘッダーの表示
    console.print(Panel(
        "[bold]OpenAI Responses API - データ分析と可視化レポート生成[/bold]\n\n"
        "このサンプルは、OpenAIのResponses APIを使用してデータ分析とインサイト抽出を\n"
        "行い、対話的なレポートを生成する方法を示しています。\n",
        title="usecase-039",
        border_style="blue"
    ))
    
    try:
        # データファイルの読み込み
        with console.status("[bold green]データを読み込み中...[/bold green]"):
            df, data_format = load_data(args.file)
        
        console.print(f"\n[bold green]データを読み込みました！[/bold green] [format: {data_format}, shape: {df.shape}]")
        
        # データプレビューの表示
        console.print("\n[bold]データプレビュー:[/bold]")
        console.print(df.head(5))
        
        # 可視化チャートの作成
        with console.status("[bold green]データの可視化を作成中...[/bold green]"):
            charts = create_visualization_charts(df)
        
        # データの分析
        console.print("\n[bold]データ分析を開始します...[/bold]")
        analysis = analyze_data(df, charts)
        
        # 分析結果の表示
        display_analysis_result(analysis)
        
        # HTMLレポートの生成
        with console.status("[bold green]HTMLレポートを生成中...[/bold green]"):
            report_path = generate_html_report(analysis, charts)
        
        console.print(f"\n[bold green]HTMLレポートを生成しました:[/bold green] {report_path}")
        
        # 対話型分析セッション
        interactive_analysis(df)
        
    except Exception as e:
        console.print(f"\n[bold red]エラーが発生しました: {e}[/bold red]")
        return
    
    console.print("\n[bold blue]分析を終了します。ありがとうございました。[/bold blue]")

if __name__ == "__main__":
    main()