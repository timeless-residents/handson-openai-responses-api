"""
フラッシュカード生成機能: 学習内容の復習用フラッシュカードを生成
"""

import json
import logging
import re
from typing import List, Dict, Any
from .ai_core import client, MOCK_MODE, logger, DEFAULT_MODEL


def generate_flashcards(
    subject: str, topic: str, level: str, num_cards: int = 10
) -> List[Dict[str, str]]:
    """指定された科目とトピックに関するフラッシュカードを生成する"""

    # プロンプトの作成
    prompt = f"次の科目とトピックについて、{level}レベルの学習者向けのフラッシュカードを{num_cards}枚作成してください。\n\n科目: {subject}\nトピック: {topic}\n\n"
    prompt += "回答は必ず以下の形式の有効なJSONとして返してください。余分なテキストは含めないでください：\n"
    prompt += "{\n"
    prompt += '  "cards": [\n'
    prompt += "    {\n"
    prompt += '      "front": "カード1の表側（質問や概念）",\n'
    prompt += '      "back": "カード1の裏側（解答や説明）"\n'
    prompt += "    },\n"
    prompt += "    {\n"
    prompt += '      "front": "カード2の表側（質問や概念）",\n'
    prompt += '      "back": "カード2の裏側（解答や説明）"\n'
    prompt += "    },\n"
    prompt += "    // 残りのカードも同様のフォーマット\n"
    prompt += "  ]\n"
    prompt += "}\n\n"
    prompt += f"必ず{num_cards}枚のカードを作成してください。各カードはfront（表側）とback（裏側）の2つのフィールドを持つ必要があります。"
    prompt += f"出力は単一のJSONオブジェクト（{{}}で囲まれたJSON）として返し、その中にcardsフィールドとして配列を含めてください。"

    # テスト環境ではダミーデータを返す
    if MOCK_MODE:
        dummy_cards = []
        for i in range(num_cards):
            card = {
                "front": f"{topic}に関する概念 {i+1}：{subject}における重要なポイント",
                "back": f"この概念の説明：{topic}は{subject}において重要な役割を果たします。特に{level}レベルでは...",
            }
            dummy_cards.append(card)
        return dummy_cards

    try:
        # OpenAI Responses APIを呼び出し - JSONフォーマットを使用
        response = client.responses.create(
            model=DEFAULT_MODEL,
            input=prompt,
            temperature=0.7,
            max_output_tokens=2000,
            # JSON形式を明示的に指定
            text={"format": {"type": "json_object"}},
        )

        # 生成された内容をJSONとしてパース
        content = response.output_text

        # JSONパースの前に詳細なデバッグログ
        logger.info(f"Flashcards raw output: {content}")
        logger.info(f"Output content type: {type(content)}")

        # 空のレスポンスの場合はデフォルト値を返す
        if not content or content.isspace():
            return [
                {
                    "front": "APIからの応答が空でした",
                    "back": "再試行するか、別のトピックを選択してください。",
                }
            ]

        # JSON文字列がスタートデリミタを持たない場合のチェック
        if (
            "{" in content
            and not content.strip().startswith("{")
            and not content.strip().startswith("[")
        ):
            content = content[content.find("{") :]

        # 不要なプレフィックスの削除
        content = content.replace("```json", "").replace("```", "")

        try:
            parsed_content = json.loads(content)

            # パース後のデータ構造をログに記録
            logger.info(f"Parsed content type: {type(parsed_content)}")
            if isinstance(parsed_content, dict):
                logger.info(f"Keys in response: {list(parsed_content.keys())}")

            # さまざまな形式に対応する処理
            if isinstance(parsed_content, list):
                # 最もシンプルなケース: 直接配列が返された
                flashcards = parsed_content
                logger.info(f"Parsed direct array with {len(flashcards)} items")
                # リストの各要素がカードかをチェック
                if (
                    len(flashcards) == 1
                    and isinstance(flashcards[0], dict)
                    and "cards" in flashcards[0]
                ):
                    # リストの最初の要素が辞書で、その中にcardsキーがある場合
                    flashcards = flashcards[0]["cards"]
                    logger.info(
                        f"Found cards array inside list item with {len(flashcards)} items"
                    )
            elif isinstance(parsed_content, dict):
                # "response"キーがある場合
                if "response" in parsed_content and isinstance(
                    parsed_content["response"], list
                ):
                    flashcards = parsed_content["response"]
                    logger.info(f"Found 'response' key with {len(flashcards)} items")
                # "flashcards"キーがある場合
                elif "flashcards" in parsed_content and isinstance(
                    parsed_content["flashcards"], list
                ):
                    flashcards = parsed_content["flashcards"]
                    logger.info(f"Found 'flashcards' key with {len(flashcards)} items")
                # "cards"キーがある場合
                elif "cards" in parsed_content and isinstance(
                    parsed_content["cards"], list
                ):
                    flashcards = parsed_content["cards"]
                    logger.info(f"Found 'cards' key with {len(flashcards)} items")
                # その他のキーがある場合は、内容を調査
                else:
                    # 最初のキーの値を取得してみる
                    first_key = next(iter(parsed_content), None)
                    if first_key and isinstance(parsed_content[first_key], list):
                        flashcards = parsed_content[first_key]
                        logger.info(
                            f"Found '{first_key}' key with {len(flashcards)} items"
                        )
                    else:
                        # 単一のカードとして扱う
                        flashcards = [parsed_content]
                        logger.info("Treating entire response as a single card")
            else:
                # 他の型の場合は空の配列
                logger.error(f"Unexpected content type: {type(parsed_content)}")
                flashcards = []
        except json.JSONDecodeError as inner_e:
            logger.error(f"JSON parse failed with error: {str(inner_e)}")
            logger.error(f"Attempted to parse: {content}")
            # 別の回避策を試す - 文字列から{}部分を抽出
            card_matches = re.findall(
                r'{\s*"front"\s*:\s*"(.*?)"\s*,\s*"back"\s*:\s*"(.*?)"\s*}',
                content,
                re.DOTALL,
            )
            if card_matches:
                flashcards = [
                    {"front": front, "back": back} for front, back in card_matches
                ]
            else:
                return [
                    {
                        "front": "JSONパースエラー",
                        "back": "APIからの応答をパースできませんでした。再試行してください。",
                    }
                ]

        # flashcards が配列でない場合は配列に変換
        if not isinstance(flashcards, list):
            if isinstance(flashcards, dict):
                # 単一のカードの場合は配列に変換
                flashcards = [flashcards]
            else:
                # 不正な形式の場合はエラーメッセージを含むカードを作成
                return [
                    {
                        "front": "フラッシュカードの生成に失敗しました",
                        "back": "APIからのレスポンスが正しい形式ではありませんでした。再試行するか、別のトピックを選択してください。",
                    }
                ]

        # 各カードの必須フィールドが存在するか確認
        validated_cards = []
        for card in flashcards:
            if isinstance(card, dict) and "front" in card and "back" in card:
                validated_cards.append(card)

        # 有効なカードが1つもない場合はデフォルトカードを返す
        if not validated_cards:
            return [
                {
                    "front": "フラッシュカードの生成に失敗しました",
                    "back": "APIからのレスポンスが有効なカードを含んでいませんでした。再試行するか、別のトピックを選択してください。",
                }
            ]

        return validated_cards

    except json.JSONDecodeError as e:
        logger.error(f"JSON パースエラー: {str(e)}")
        logger.error(f"受信内容: {content}")
        # フォールバック：エラーメッセージを含むカードを返す
        return [
            {
                "front": "フラッシュカードの生成中にJSONエラーが発生しました",
                "back": f"APIからのレスポンスがJSON形式ではありませんでした。再試行するか、別のトピックを選択してください。エラー: {str(e)}",
            }
        ]
    except Exception as e:
        logger.error(f"OpenAI API 呼び出しエラー: {str(e)}")
        # フォールバック：エラーメッセージを含むカードを返す
        return [
            {
                "front": "フラッシュカードの生成中にエラーが発生しました",
                "back": f"APIリクエスト中にエラーが発生しました。再試行するか、別のトピックを選択してください。エラー: {str(e)}",
            }
        ]
