"""
クイズ生成機能: 学習内容のテスト用クイズ問題を生成
"""

import json
import logging
import re
from typing import List, Dict, Any
from .ai_core import client, MOCK_MODE, logger, DEFAULT_MODEL


def generate_quiz_questions(
    subject: str, topic: str, level: str, num_questions: int = 5
) -> List[Dict[str, Any]]:
    """指定された科目とトピックに関するクイズの問題を生成する"""

    # プロンプトの作成
    prompt = (
        f"あなたは学習クイズ生成AIです。次の科目とトピックについて、{level}レベルの学習者向けのクイズ問題を{num_questions}問作成してください。\n\n"
        f"科目: {subject}\nトピック: {topic}\n\n"
    )
    prompt += "以下の形式の有効なJSONオブジェクト（正確に指定された構造に従ってください）で回答してください：\n"
    prompt += "{\n"
    prompt += '  "questions": [\n'
    prompt += "    {\n"
    prompt += '      "question": "問題文1",\n'
    prompt += '      "options": ["選択肢1-1", "選択肢1-2", "選択肢1-3", "選択肢1-4"],\n'
    prompt += '      "answer": "選択肢1-X（正解の選択肢の完全なテキスト）",\n'
    prompt += '      "explanation": "問題1と解答の説明"\n'
    prompt += "    },\n"
    prompt += "    {\n"
    prompt += '      "question": "問題文2",\n'
    prompt += '      "options": ["選択肢2-1", "選択肢2-2", "選択肢2-3", "選択肢2-4"],\n'
    prompt += '      "answer": "選択肢2-X（正解の選択肢の完全なテキスト）",\n'
    prompt += '      "explanation": "問題2と解答の説明"\n'
    prompt += "    }\n"
    prompt += "  ]\n"
    prompt += "}\n\n"
    prompt += f"必ず{num_questions}問の問題を作成し、questionsキーの配列として含めてください。各問題は4つの選択肢を持ち、1つの正解と説明を含める必要があります。"
    prompt += "JSONオブジェクトは正確に上記の形式に従い、追加のコメントや説明なしで返してください。"

    if MOCK_MODE:
        dummy_questions = []
        for i in range(num_questions):
            question = {
                "question": f"{topic}に関する問題 {i+1}：この問題の正解は選択肢{i % 4 + 1}です。",
                "options": [
                    f"選択肢1: {topic}の説明1",
                    f"選択肢2: {topic}の説明2",
                    f"選択肢3: {topic}の説明3",
                    f"選択肢4: {topic}の説明4",
                ],
                "answer": f"選択肢{i % 4 + 1}: {topic}の説明{i % 4 + 1}",
                "explanation": f"この問題では{topic}の理解度を確認しています。正解は選択肢{i % 4 + 1}です。なぜなら...",
            }
            dummy_questions.append(question)
        return dummy_questions

    try:
        response = client.responses.create(
            model=DEFAULT_MODEL,
            input=prompt,
            temperature=0.7,
            max_output_tokens=3000,
            text={"format": {"type": "json_object"}},
        )
        content = response.output_text
        logger.info(f"Quiz questions raw output: {content[:100]}...")

        if not content or content.isspace():
            return [
                {
                    "question": "APIからの応答が空でした",
                    "options": ["選択肢1", "選択肢2", "選択肢3", "選択肢4"],
                    "answer": "選択肢1",
                    "explanation": "再試行するか、別のトピックを選択してください。",
                }
            ]

        content = content.replace("```json", "").replace("```", "")
        if not content.strip().startswith("["):
            content = f"[{content}]"
        if (
            "{" in content
            and not content.strip().startswith("{")
            and not content.strip().startswith("[")
        ):
            content = content[content.find("{") :]

        try:
            parsed_content = json.loads(content)
            logger.info(f"Parsed content type: {type(parsed_content)}")
            
            # 解析されたレスポンスをログに記録
            if isinstance(parsed_content, dict):
                logger.info(f"Response keys: {list(parsed_content.keys())}")
            
            # questionsリストを取得
            questions = []
            
            # ケース1: 直接リストが返された場合
            if isinstance(parsed_content, list):
                questions = parsed_content
                logger.info(f"Direct list of questions: {len(questions)} items")
            
            # ケース2: {questions: [...]} 形式
            elif isinstance(parsed_content, dict) and "questions" in parsed_content:
                if isinstance(parsed_content["questions"], list):
                    questions = parsed_content["questions"]
                    logger.info(f"Found 'questions' array with {len(questions)} items")
                else:
                    questions = [parsed_content["questions"]]  # リストでなければリストに変換
                    logger.info("Found 'questions' non-array value, converted to list")
            
            # ケース3: その他のキーを探す
            elif isinstance(parsed_content, dict):
                for key in ("result", "message", "quizzes", "quiz", "data"):
                    if key in parsed_content and isinstance(parsed_content[key], list):
                        questions = parsed_content[key]
                        logger.info(f"Found '{key}' array with {len(questions)} items")
                        break
            
            # 入れ子のquestions配列を処理
            if (len(questions) == 1 and isinstance(questions[0], dict) and 
                "questions" in questions[0] and isinstance(questions[0]["questions"], list)):
                questions = questions[0]["questions"]
                logger.info(f"Extracted nested questions array with {len(questions)} items")
            
            logger.info(f"Extracted questions: {questions}")

        except Exception as parse_e:
            logger.error(f"Error processing response: {str(parse_e)}")
            logger.error(f"Response content: {content}")
            return [
                {
                    "question": "レスポンス処理中にエラーが発生しました",
                    "options": ["選択肢1", "選択肢2", "選択肢3", "選択肢4"],
                    "answer": "選択肢1",
                    "explanation": f"APIレスポンスの処理中にエラーが発生しました: {str(parse_e)}",
                }
            ]
            
        if not isinstance(questions, list):
            return [
                {
                    "question": "生成された問題の形式が正しくありませんでした。再試行してください。",
                    "options": ["選択肢1", "選択肢2", "選択肢3", "選択肢4"],
                    "answer": "選択肢1",
                    "explanation": "APIからのレスポンスが正しい形式ではありませんでした。再試行するか、別のトピックを選択してください。",
                }
            ]

        validated_questions = []
        for q in questions:
            # 直接 "question" と "options" がある場合
            if isinstance(q, dict) and "question" in q and "options" in q:
                if "answer" not in q:
                    q["answer"] = "回答が提供されていません。"
                if "explanation" not in q:
                    q["explanation"] = "解説が提供されていません。"
                if not isinstance(q.get("options"), list):
                    q["options"] = ["選択肢1", "選択肢2", "選択肢3", "選択肢4"]
                validated_questions.append(q)
            # もし q の中に "quiz" または "quizzes" キーが存在するなら展開
            elif isinstance(q, dict):
                for sub_key in ("quiz", "quizzes"):
                    if sub_key in q and isinstance(q[sub_key], list):
                        for sub_q in q[sub_key]:
                            if (
                                isinstance(sub_q, dict)
                                and "question" in sub_q
                                and "options" in sub_q
                            ):
                                if "answer" not in sub_q:
                                    sub_q["answer"] = "回答が提供されていません。"
                                if "explanation" not in sub_q:
                                    sub_q["explanation"] = "解説が提供されていません。"
                                if not isinstance(sub_q.get("options"), list):
                                    sub_q["options"] = [
                                        "選択肢1",
                                        "選択肢2",
                                        "選択肢3",
                                        "選択肢4",
                                    ]
                                validated_questions.append(sub_q)
                            else:
                                logger.info(
                                    f"Sub-question keys: {list(sub_q.keys()) if isinstance(sub_q, dict) else type(sub_q)}"
                                )
                        break
            else:
                logger.info(f"Skipped non-dict question item: {q}")

        logger.info(f"Validated quiz questions count: {len(validated_questions)}")
        if not validated_questions:
            return [
                {
                    "question": "生成された問題が有効ではありませんでした。再試行してください。",
                    "options": ["選択肢1", "選択肢2", "選択肢3", "選択肢4"],
                    "answer": "選択肢1",
                    "explanation": "APIからのレスポンスが有効な問題を含んでいませんでした。再試行するか、別のトピックを選択してください。",
                }
            ]

        return validated_questions

    except json.JSONDecodeError as e:
        logger.error(f"JSON パースエラー: {str(e)}")
        logger.error(f"受信内容: {content}")
        return [
            {
                "question": "生成された問題の形式が正しくありませんでした。再試行してください。",
                "options": ["選択肢1", "選択肢2", "選択肢3", "選択肢4"],
                "answer": "選択肢1",
                "explanation": "APIからのレスポンスがJSON形式ではありませんでした。再試行するか、別のトピックを選択してください。",
            }
        ]
    except Exception as e:
        logger.error(f"OpenAI API 呼び出しエラー: {str(e)}")
        return [
            {
                "question": f"問題の生成中にエラーが発生しました: {str(e)}",
                "options": [
                    "再試行する",
                    "別のトピックを選択する",
                    "少し待ってから試す",
                    "管理者に連絡する",
                ],
                "answer": "再試行する",
                "explanation": "APIリクエスト中にエラーが発生しました。再試行するか、別のトピックを選択してください。",
            }
        ]


