"""
AIチャット機能: 会話形式での学習支援
"""

import logging
from typing import List, Dict, Optional
from .ai_core import client, MOCK_MODE, logger, DEFAULT_MODEL


def ask_ai_tutor(
    messages: List[Dict[str, str]],
    subject: Optional[str] = None,
    topic: Optional[str] = None,
) -> str:
    """AIチューターに質問して回答を得る"""

    # システムプロンプト（instructions）の作成
    instructions = "あなたは親切で役立つAI学習アシスタントです。"

    if subject:
        instructions += f" 特に{subject}の分野の質問に詳しく回答できます。"

    if topic:
        instructions += f" 今回の会話では{topic}について焦点を当てています。"

    instructions += " 明確で正確な情報を提供し、学習者の理解を深めるために例を示したり、ステップバイステップの説明を行ったりしてください。"

    # テスト環境ではダミーレスポンスを返す
    if MOCK_MODE:
        # 最新のユーザーメッセージを取得
        user_message = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                user_message = msg["content"]
                break

        # 簡単な応答を生成
        response_text = f"""
こんにちは！AI学習アシスタントです。

あなたの質問：「{user_message[:50]}...」について回答します。

{subject or 'この分野'}における{topic or 'このトピック'}は非常に重要です。主なポイントは以下の通りです：

1. 基本概念を理解することが重要です
2. 実践的な例を通じて学ぶことで理解が深まります
3. 繰り返し練習することでスキルが向上します

さらに詳しい情報が必要であれば、具体的にお知らせください。
"""
        return response_text

    try:
        # 会話履歴からユーザー入力を抽出
        conversation_history = []
        last_user_message = ""

        for msg in messages:
            if msg["role"] == "user":
                conversation_history.append({"role": "user", "content": msg["content"]})
                last_user_message = msg["content"]
            elif msg["role"] == "assistant":
                conversation_history.append(
                    {"role": "assistant", "content": msg["content"]}
                )

        # 会話履歴がある場合は、過去の会話をinputとして渡し、instructionsでAIの役割を指定
        if len(conversation_history) > 1:
            # 最新のユーザーメッセージを除いた会話履歴をconversation_historyとして渡す
            past_conversation = (
                conversation_history[:-1]
                if conversation_history[-1]["role"] == "user"
                else conversation_history
            )

            # 会話履歴を使ってメッセージ配列を作成
            messages_for_api = [{"role": "system", "content": instructions}]
            
            # 会話履歴を追加 (past_conversationは最新メッセージを除く)
            for msg in past_conversation:
                messages_for_api.append(msg)
            
            # 最新のメッセージを追加
            messages_for_api.append({"role": "user", "content": last_user_message})
                
            # APIを呼び出し
            response = client.responses.create(
                model=DEFAULT_MODEL,
                input=messages_for_api,
                temperature=0.7,
                max_output_tokens=2000,
            )
        else:
            # 初回メッセージの場合 - システムプロンプトとユーザーメッセージのみ
            messages_for_api = [
                {"role": "system", "content": instructions},
                {"role": "user", "content": last_user_message}
            ]
            response = client.responses.create(
                model=DEFAULT_MODEL,
                input=messages_for_api,
                temperature=0.7,
                max_output_tokens=2000,
            )

        # 生成された回答を返す
        return response.output_text
    except Exception as e:
        logger.error(f"OpenAI API 呼び出しエラー: {str(e)}")
        return "回答の生成中にエラーが発生しました。しばらくしてからもう一度お試しください。"
