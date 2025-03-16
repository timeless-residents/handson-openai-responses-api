"""
学習コンテンツ生成機能: 説明、要約、学習プランなどの生成を担当
"""

import json
import logging
from typing import Dict, Any, List, Optional
from .ai_core import client, MOCK_MODE, logger, DEFAULT_MODEL


def generate_learning_content(
    subject: str, topic: str, level: str, content_type: str = "explanation"
) -> str:
    """指定された科目とトピックに関する学習コンテンツを生成する"""

    # プロンプトの作成
    if content_type == "explanation":
        prompt = f"次の科目とトピックについて、{level}レベルの学習者向けの説明を作成してください。\n\n科目: {subject}\nトピック: {topic}\n\n"
        prompt += "説明は以下の条件を満たすようにしてください：\n"
        prompt += "- 明確で理解しやすい言葉を使用\n"
        prompt += "- 適切な例を含める\n"
        prompt += "- 重要な概念を強調\n"
        prompt += "- Markdown形式で返答してください。見出し、リスト、強調などを適切に使用してください。\n"
    elif content_type == "examples":
        prompt = f"次の科目とトピックについて、{level}レベルの学習者向けの例題と解答を4つ作成してください。\n\n科目: {subject}\nトピック: {topic}\n\n"
        prompt += "例題と解答は以下の条件を満たすようにしてください：\n"
        prompt += "- 実践的で理解を深める例題\n"
        prompt += "- 詳細な解説付きの解答\n"
        prompt += "- 難易度は徐々に上げる\n"
        prompt += "- Markdown形式で返答してください。例題ごとに見出しを使い、コードブロックなどを適切に使用してください。\n"
    elif content_type == "summary":
        prompt = f"次の科目とトピックについて、{level}レベルの学習者向けの要点まとめを作成してください。\n\n科目: {subject}\nトピック: {topic}\n\n"
        prompt += "要点まとめは以下の条件を満たすようにしてください：\n"
        prompt += "- 重要な概念を箇条書きで簡潔に\n"
        prompt += "- 関連する用語の定義\n"
        prompt += "- 覚えておくべきポイントを強調\n"
        prompt += "- Markdown形式で返答してください。見出しとリストを適切に使用してください。\n"
    elif content_type == "assessment":
        prompt = f"次の科目とトピックについて、{level}レベルの学習者向けの小テスト問題を5つ作成してください。\n\n科目: {subject}\nトピック: {topic}\n\n"
        prompt += "問題は以下の条件を満たすようにしてください：\n"
        prompt += "- 選択肢問題と記述問題の混合\n"
        prompt += "- 理解度を測定するための適切な難易度\n"
        prompt += "- 各問題に解答と簡単な解説を含める\n"
        prompt += "- Markdown形式で返答してください。問題ごとに見出しを使い、選択肢はリスト形式で表示してください。\n"
    else:
        prompt = f"次の科目とトピックについて、{level}レベルの学習者向けの学習コンテンツを作成してください。\n\n科目: {subject}\nトピック: {topic}\n\n"

    # テスト環境ではダミーレスポンスを返す
    if MOCK_MODE:
        if content_type == "explanation":
            return f"""
# {topic}の基本概念

{topic}は{subject}の重要な概念です。以下にその主要なポイントを説明します。

## 主要な特徴

- 特徴1: {topic}の基本的な性質について
- 特徴2: 応用例と使用場面
- 特徴3: 他の概念との関連性

## 実践的な応用

{topic}を実際に使用する際のポイントは以下の通りです：

1. まず基本を理解する
2. 簡単な例題で練習する
3. 徐々に複雑な問題に挑戦する

> 重要: {topic}を学ぶ際は実践することが最も効果的です！

## まとめ

{topic}は{level}レベルの学習者にとって重要な概念であり、しっかりと理解することで{subject}の理解が深まります。
"""
        else:
            return f"# {topic}に関する{content_type}\n\n{subject}の{level}レベルの内容です。\n\n## 要点1\n\n具体的な説明が入ります。\n\n## 要点2\n\n詳細な解説がここに入ります。"

    try:
        # OpenAI Responses APIを呼び出し
        response = client.responses.create(
            model=DEFAULT_MODEL, input=prompt, temperature=0.7, max_output_tokens=2000
        )

        # 生成されたコンテンツを返す
        return response.output_text
    except Exception as e:
        logger.error(f"OpenAI API 呼び出しエラー: {str(e)}")
        return "コンテンツの生成中にエラーが発生しました。しばらくしてからもう一度お試しください。"


def generate_learning_plan(
    subject: str, topic: Optional[str], level: str, duration_days: int = 30
) -> Dict[str, Any]:
    """指定された科目とトピックに関する学習プランを生成する"""

    # プロンプトの作成
    prompt = f"次の科目について、{level}レベルの学習者向けの{duration_days}日間の学習プランを作成してください。\n\n科目: {subject}\n"

    if topic:
        prompt += f"特に焦点を当てるトピック: {topic}\n\n"

    prompt += "回答は必ず以下の形式の有効なJSONとして返してください。余分なテキストは含めないでください：\n"
    prompt += "{\n"
    prompt += '  "title": "学習プランのタイトル",\n'
    prompt += '  "description": "学習プランの説明と目標",\n'
    prompt += '  "items": [\n'
    prompt += "    {\n"
    prompt += '      "title": "項目1のタイトル",\n'
    prompt += '      "description": "項目1の詳細説明",\n'
    prompt += '      "order": 1\n'
    prompt += "    },\n"
    prompt += "    {\n"
    prompt += '      "title": "項目2のタイトル",\n'
    prompt += '      "description": "項目2の詳細説明",\n'
    prompt += '      "order": 2\n'
    prompt += "    },\n"
    prompt += "    // 残りの項目も同様のフォーマット\n"
    prompt += "  ]\n"
    prompt += "}\n\n"
    prompt += f"項目は各学習ステップを表します。必ず10個以上の項目を含め、順番に学習を進めるための論理的な順序にしてください。\n"
    prompt += (
        f"各項目には必ずtitle、description、orderの3つのフィールドを含めてください。\n"
    )
    prompt += f"出力は単一のJSONオブジェクト（{{}}で囲まれたJSON）として返し、itemsフィールドには項目の配列（[]で囲まれたJSON）を含めてください。"

    # テスト環境ではダミーデータを返す
    if MOCK_MODE:
        topic_str = topic or subject
        plan_items = []
        for i in range(10):
            plan_items.append(
                {
                    "title": f"ステップ {i+1}: {topic_str}の{['基礎','応用','実践'][i%3]}学習",
                    "description": f"このステップでは{topic_str}の{['基本概念','応用技術','実践的な使い方'][i%3]}について学びます。{duration_days//10}日間かけて取り組みましょう。",
                    "order": i + 1,
                }
            )

        return {
            "title": f"{subject}の{level}レベル学習プラン",
            "description": f"この学習プランは{level}レベルの学習者向けに{subject}を学ぶための{duration_days}日間のガイドです。"
            + (f"特に{topic}に焦点を当てています。" if topic else "")
            + "各ステップを順番に進めることで、効率的に知識を身につけることができます。",
            "items": plan_items,
        }

    try:
        # OpenAI Responses APIを呼び出し（JSON形式の指定なし - 純粋なテキスト）
        response = client.responses.create(
            model=DEFAULT_MODEL,
            input=prompt,
            temperature=0.7,
            max_output_tokens=3000,
            # JSON形式の指定を削除し、純粋なテキスト出力を使用
        )

        # 生成された内容をJSONとしてパース
        content = response.output_text
        plan = json.loads(content)

        # 必須フィールドの検証と、必要に応じてデフォルト値の設定
        if not isinstance(plan, dict):
            return {
                "title": f"{subject}の学習プラン",
                "description": "学習プランの生成中に形式エラーが発生しました。別のトピックを試してください。",
                "items": get_default_plan_items(subject, topic, level, duration_days),
            }

        # 必須フィールドの存在確認
        if "title" not in plan:
            plan["title"] = f"{subject}の{level}レベル学習プラン"

        if "description" not in plan:
            topic_text = f"トピック「{topic}」に焦点を当てた" if topic else ""
            plan["description"] = (
                f"{topic_text}{subject}の{level}レベル学習プランです。{duration_days}日間で効率的に学習を進めていきましょう。"
            )

        # items フィールドの検証
        if (
            "items" not in plan
            or not isinstance(plan["items"], list)
            or len(plan["items"]) == 0
        ):
            plan["items"] = get_default_plan_items(subject, topic, level, duration_days)
        else:
            # 各項目の必須フィールドの検証
            validated_items = []
            for i, item in enumerate(plan["items"]):
                if not isinstance(item, dict):
                    continue

                valid_item = {}
                valid_item["title"] = item.get(
                    "title", f"ステップ {i+1}: {subject}の学習"
                )
                valid_item["description"] = item.get(
                    "description", "このステップの詳細説明がありません。"
                )
                valid_item["order"] = item.get("order", i + 1)

                validated_items.append(valid_item)

            if not validated_items:
                plan["items"] = get_default_plan_items(
                    subject, topic, level, duration_days
                )
            else:
                plan["items"] = validated_items

        return plan

    except json.JSONDecodeError as e:
        logger.error(f"JSON パースエラー: {str(e)}")
        logger.error(f"受信内容: {content}")
        return {
            "title": f"{subject}の学習プラン",
            "description": f"学習プランの生成中にJSONパースエラーが発生しました: {str(e)}",
            "items": get_default_plan_items(subject, topic, level, duration_days),
        }
    except Exception as e:
        logger.error(f"OpenAI API 呼び出しエラー: {str(e)}")
        return {
            "title": f"{subject}の{level}レベル学習プラン",
            "description": f"学習プランの生成中にエラーが発生しました: {str(e)}",
            "items": get_default_plan_items(subject, topic, level, duration_days),
        }


def get_default_plan_items(subject, topic, level, duration_days):
    """デフォルトの学習プラン項目を生成"""
    topic_str = topic or subject
    plan_items = []
    steps = [
        ("基礎学習", "基本概念と用語を理解します"),
        ("基礎的な例題", "簡単な例題を解いて基礎を固めます"),
        ("中級の概念", "より高度な概念を学びます"),
        ("応用練習", "応用問題に取り組みます"),
        ("アプリケーション", "学んだ知識を実際に応用します"),
        ("高度な技術", "専門的な技術を習得します"),
        ("プロジェクト作成", "学んだ内容を活かしたプロジェクトに取り組みます"),
        ("復習と統合", "これまでの学習内容を復習して知識を統合します"),
        ("発展学習", "より高度な内容に挑戦します"),
        ("最終評価", "学習の成果を確認します"),
    ]

    for i, (step_title, step_desc) in enumerate(steps):
        if i < 10:  # 最大10項目
            plan_items.append(
                {
                    "title": f"ステップ {i+1}: {topic_str}の{step_title}",
                    "description": f"{step_desc}。{topic_str}について{level}レベルの理解を深めます。",
                    "order": i + 1,
                }
            )

    return plan_items


def summarize_text(text: str) -> str:
    """テキストを要約する"""

    # プロンプトの作成
    prompt = "以下のテキストを要約してください。重要なポイントを保持しながら、できるだけ簡潔にまとめてください。\n\n"
    prompt += text

    # テスト環境ではダミーレスポンスを返す
    if MOCK_MODE:
        # テキストの長さに応じて要約の長さを調整
        text_length = len(text)
        if text_length < 100:
            return text

        # 非常に簡易的な要約処理
        sentences = text.split("。")
        if len(sentences) <= 3:
            return text

        # 最初と最後の文を取得して結合
        summary = sentences[0] + "。"
        if len(sentences) > 1:
            middle_idx = len(sentences) // 2
            summary += sentences[middle_idx] + "。"
        summary += sentences[-2] + "。"

        return summary

    try:
        # OpenAI Responses APIを呼び出し
        response = client.responses.create(
            model=DEFAULT_MODEL, input=prompt, temperature=0.3, max_output_tokens=500
        )

        # 生成された要約を返す
        return response.output_text
    except Exception as e:
        logger.error(f"OpenAI API 呼び出しエラー: {str(e)}")
        return "テキストの要約中にエラーが発生しました。"
