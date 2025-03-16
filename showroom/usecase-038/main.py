#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
usecase-038: メディア内容のモデレーションと分類

Responses APIを使用してテキストコンテンツを分析し、
安全性チェックやカテゴリ分類を行うサンプルコード。
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List

import openai
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

# 環境変数の読み込み
dotenv_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path)

# APIキーの設定
openai.api_key = os.getenv("OPENAI_API_KEY")

# コンソール設定
console = Console()

# コンテンツポリシー定義
CONTENT_POLICY = """
# コンテンツポリシー
以下のカテゴリに該当するコンテンツは禁止または制限されています:

1. 有害コンテンツ: 暴力、自傷行為、危険行為の促進
2. ヘイトスピーチ: 差別、人種差別、性差別など
3. 性的コンテンツ: 露骨な性的表現、未成年者に関する不適切なコンテンツ
4. 詐欺的コンテンツ: 虚偽情報、詐欺、フィッシング
5. プライバシー侵害: 個人情報の無断公開
6. 著作権侵害: 無許可の著作物使用
7. スパム: 大量の無関係コンテンツ、広告

各カテゴリには重大度レベルがあります:
- 低: 軽微な違反、警告対象
- 中: 明確な違反、コンテンツ削除対象
- 高: 深刻な違反、アカウント停止対象
"""

# サンプルテキスト
SAMPLE_TEXTS = [
    "今日は素晴らしい一日でした。公園を散歩して、友人と食事を楽しみました。",
    "この製品は最低です。二度と買いません。販売員も無礼でした。",
    "@username の住所は123 Main St.で、電話番号は555-1234です。みんなでいたずら電話しましょう。",
    "彼らの民族は全て同じです。この国から出て行くべきです。",
    "安い値段で高級腕時計を販売中！今だけ90%オフ。詳細はこのリンクをクリック: bit.ly/2ZjGd",
]


def create_moderation_request(content: str) -> Dict[str, Any]:
    """モデレーションリクエストを作成"""
    # リクエストの作成
    return {
        "model": "gpt-4o",
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": f"""あなたはコンテンツモデレーターです。テキストを分析し、コンテンツポリシーに基づいて分類してください。

{CONTENT_POLICY}

以下の形式のJSONで回答してください:
{{
  "category": "安全" または "要注意" または "違反",
  "categories": ["有害コンテンツ", "ヘイトスピーチ", "性的コンテンツ", "詐欺的コンテンツ", "プライバシー侵害", "著作権侵害", "スパム", "なし"] のうち該当するものの配列,
  "severity": "低" または "中" または "高" または "なし",
  "explanation": "説明文",
  "recommendation": "推奨対応"
}}""",
            },
            {
                "role": "user",
                "content": f"以下のテキストを分析し、コンテンツポリシーに照らして評価してください:\n\n{content}",
            },
        ],
    }


def analyze_content(content: str) -> Dict[str, Any]:
    """コンテンツを分析してモデレーション結果を返す"""
    try:
        # OpenAI APIにリクエスト送信
        request = create_moderation_request(content)
        response = openai.chat.completions.create(**request)

        # JSONレスポンスを解析
        result = json.loads(response.choices[0].message.content)
        return result

    except Exception as e:
        console.print(f"[bold red]エラーが発生しました: {e}[/bold red]")
        return {
            "category": "エラー",
            "categories": ["エラー"],
            "severity": "なし",
            "explanation": f"分析中にエラーが発生しました: {str(e)}",
            "recommendation": "システム管理者に連絡してください。",
        }


def display_analysis_result(content: str, result: Dict[str, Any]) -> None:
    """分析結果を表示"""
    # カテゴリに基づいて色を選択
    category_colors = {
        "安全": "green",
        "要注意": "yellow",
        "違反": "red",
        "エラー": "red",
    }

    color = category_colors.get(result["category"], "white")

    # 結果パネルの作成
    console.print(
        Panel(
            f"[bold]{content}[/bold]\n\n"
            f"[bold]カテゴリ:[/bold] [{color}]{result['category']}[/{color}]\n"
            f"[bold]検出カテゴリ:[/bold] {', '.join(result['categories'])}\n"
            f"[bold]重大度:[/bold] {result['severity']}\n\n"
            f"[bold]説明:[/bold]\n{result['explanation']}\n\n"
            f"[bold]推奨対応:[/bold]\n{result['recommendation']}",
            title=f"コンテンツ分析結果",
            border_style=color,
        )
    )


def analyze_custom_content() -> None:
    """ユーザー入力のコンテンツを分析"""
    console.print(
        "\n[bold]分析したいテキストを入力してください (終了するには 'exit' と入力):[/bold]"
    )

    while True:
        content = console.input("\n>> ")

        if content.lower() == "exit":
            break

        with console.status("[bold green]コンテンツを分析中...[/bold green]"):
            result = analyze_content(content)

        display_analysis_result(content, result)


def main() -> None:
    """メイン関数"""
    console.print(
        Panel(
            "[bold]OpenAI Responses API - メディア内容のモデレーションと分類[/bold]\n\n"
            "このサンプルは、OpenAIのResponses APIを使用してテキストコンテンツの\n"
            "モデレーションと分類を行う方法を示しています。\n",
            title="usecase-038",
            border_style="blue",
        )
    )

    # コンテンツポリシーの表示
    console.print(Markdown(CONTENT_POLICY))

    # サンプルテキストの分析
    console.print("\n[bold]サンプルテキストの分析:[/bold]\n")

    for i, text in enumerate(SAMPLE_TEXTS, 1):
        console.print(f"\n[bold]サンプル {i}:[/bold]")

        with console.status(f"[bold green]サンプル {i} を分析中...[/bold green]"):
            result = analyze_content(text)
            time.sleep(0.5)  # UIの見栄えのための短い遅延

        display_analysis_result(text, result)

    # カスタムコンテンツの分析
    analyze_custom_content()

    console.print("\n[bold blue]分析を終了します。ありがとうございました。[/bold blue]")


if __name__ == "__main__":
    main()
