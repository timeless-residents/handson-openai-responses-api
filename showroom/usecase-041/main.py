"""
医療情報の理解支援と説明

このサンプルは、OpenAI Responses APIを使用した医療情報理解支援アシスタントを実装しています。
専門的な医療用語や情報を一般の方にもわかりやすく説明し、健康リテラシーの向上をサポートします。
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import openai
from flask import Flask, request, jsonify, render_template

# 医療情報データを管理するモジュール
from medical_data import (
    get_medical_term,
    search_medical_terms,
    get_symptom_info,
    search_symptoms,
    get_treatment_info,
    search_treatments,
    get_healthcare_system_info,
    search_healthcare_systems,
    get_prevention_info,
    get_faq,
)

# Python 3.7以降の場合、標準入出力のエンコーディングをUTF-8に設定
if sys.version_info >= (3, 7):
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")


def setup_environment():
    """環境設定を行い、APIキーを取得します。"""
    # プロジェクトのルートディレクトリの.envファイルを読み込む
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(script_dir))
    load_dotenv(os.path.join(root_dir, ".env"))

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY が設定されていません")
    return api_key


# --- ツール関数のモデル定義 ---


class MedicalTermRequest(BaseModel):
    """医療用語情報取得のリクエストモデル"""

    term_id: str = Field(..., description="医療用語ID（例: TERM-001）")


class SearchMedicalTermsRequest(BaseModel):
    """医療用語検索のリクエストモデル"""

    query: str = Field(..., description="検索キーワード")
    category: Optional[str] = Field(
        None,
        description="用語カテゴリ（anatomy:解剖学, disease:疾病, test:検査, treatment:治療）",
    )


class SymptomInfoRequest(BaseModel):
    """症状情報取得のリクエストモデル"""

    symptom_id: str = Field(..., description="症状ID（例: SYMP-001）")


class SearchSymptomsRequest(BaseModel):
    """症状検索のリクエストモデル"""

    query: str = Field(..., description="検索キーワード")
    body_part: Optional[str] = Field(
        None,
        description="身体部位（head:頭部, chest:胸部, abdomen:腹部, limbs:四肢, skin:皮膚）",
    )


class TreatmentInfoRequest(BaseModel):
    """治療法情報取得のリクエストモデル"""

    treatment_id: str = Field(..., description="治療法ID（例: TRT-001）")


class SearchTreatmentsRequest(BaseModel):
    """治療法検索のリクエストモデル"""

    query: str = Field(..., description="検索キーワード")
    treatment_type: Optional[str] = Field(
        None,
        description="治療タイプ（medication:薬物治療, surgery:手術, physical:理学療法, mental:精神療法）",
    )


class HealthcareSystemInfoRequest(BaseModel):
    """医療制度情報取得のリクエストモデル"""

    system_id: str = Field(..., description="制度ID（例: SYS-001）")


class SearchHealthcareSystemsRequest(BaseModel):
    """医療制度検索のリクエストモデル"""

    query: str = Field(..., description="検索キーワード")
    system_type: Optional[str] = Field(
        None,
        description="制度タイプ（insurance:保険, subsidy:助成, welfare:福祉, service:サービス）",
    )


class PreventionInfoRequest(BaseModel):
    """予防医学情報取得のリクエストモデル"""

    disease_type: Optional[str] = Field(
        None,
        description="疾患タイプ（lifestyle:生活習慣病, infectious:感染症, mental:精神疾患, other:その他）",
    )


class FaqRequest(BaseModel):
    """FAQ検索のリクエストモデル"""

    query: Optional[str] = Field(
        None, description="検索キーワード（指定しない場合は全FAQを取得）"
    )
    category: Optional[str] = Field(
        None,
        description="カテゴリ（general:一般, medication:薬, examination:検査, insurance:保険）",
    )


# --- ツール定義 ---


def setup_tools():
    """ツール定義を設定します。"""
    return [
        {
            "type": "function",
            "name": "get_medical_term",
            "description": "医療用語IDを指定して医療用語の詳細説明を取得します",
            "parameters": {
                "type": "object",
                "properties": {
                    "term_id": {
                        "type": "string",
                        "description": "医療用語ID（例: TERM-001）",
                    }
                },
                "required": ["term_id"],
            },
        },
        {
            "type": "function",
            "name": "search_medical_terms",
            "description": "キーワードで医療用語を検索します",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "検索キーワード"},
                    "category": {
                        "type": "string",
                        "description": "用語カテゴリ（anatomy:解剖学, disease:疾病, test:検査, treatment:治療）",
                    },
                },
                "required": ["query"],
            },
        },
        {
            "type": "function",
            "name": "get_symptom_info",
            "description": "症状IDを指定して症状の詳細情報を取得します",
            "parameters": {
                "type": "object",
                "properties": {
                    "symptom_id": {
                        "type": "string",
                        "description": "症状ID（例: SYMP-001）",
                    }
                },
                "required": ["symptom_id"],
            },
        },
        {
            "type": "function",
            "name": "search_symptoms",
            "description": "キーワードで症状を検索します",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "検索キーワード"},
                    "body_part": {
                        "type": "string",
                        "description": "身体部位（head:頭部, chest:胸部, abdomen:腹部, limbs:四肢, skin:皮膚）",
                    },
                },
                "required": ["query"],
            },
        },
        {
            "type": "function",
            "name": "get_treatment_info",
            "description": "治療法IDを指定して治療法の詳細情報を取得します",
            "parameters": {
                "type": "object",
                "properties": {
                    "treatment_id": {
                        "type": "string",
                        "description": "治療法ID（例: TRT-001）",
                    }
                },
                "required": ["treatment_id"],
            },
        },
        {
            "type": "function",
            "name": "search_treatments",
            "description": "キーワードで治療法を検索します",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "検索キーワード"},
                    "treatment_type": {
                        "type": "string",
                        "description": "治療タイプ（medication:薬物治療, surgery:手術, physical:理学療法, mental:精神療法）",
                    },
                },
                "required": ["query"],
            },
        },
        {
            "type": "function",
            "name": "get_healthcare_system_info",
            "description": "医療制度IDを指定して医療制度の詳細情報を取得します",
            "parameters": {
                "type": "object",
                "properties": {
                    "system_id": {
                        "type": "string",
                        "description": "制度ID（例: SYS-001）",
                    }
                },
                "required": ["system_id"],
            },
        },
        {
            "type": "function",
            "name": "search_healthcare_systems",
            "description": "キーワードで医療制度を検索します",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "検索キーワード"},
                    "system_type": {
                        "type": "string",
                        "description": "制度タイプ（insurance:保険, subsidy:助成, welfare:福祉, service:サービス）",
                    },
                },
                "required": ["query"],
            },
        },
        {
            "type": "function",
            "name": "get_prevention_info",
            "description": "予防医学の情報を取得します",
            "parameters": {
                "type": "object",
                "properties": {
                    "disease_type": {
                        "type": "string",
                        "description": "疾患タイプ（lifestyle:生活習慣病, infectious:感染症, mental:精神疾患, other:その他）",
                    }
                },
            },
        },
        {
            "type": "function",
            "name": "get_faq",
            "description": "医療に関するよくある質問（FAQ）を検索します",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "検索キーワード"},
                    "category": {
                        "type": "string",
                        "description": "カテゴリ（general:一般, medication:薬, examination:検査, insurance:保険）",
                    },
                },
            },
        },
    ]


# --- チャットボット処理関数 ---


def process_chat(client, user_message, conversation_history=None):
    """
    ユーザーからのメッセージを処理し、適切な応答を生成します。

    Args:
        client (openai.Client): OpenAIクライアント
        user_message (str): ユーザーからのメッセージ
        conversation_history (list, optional): 過去の会話履歴

    Returns:
        dict: 応答メッセージとステータス
    """
    tools = setup_tools()
    instructions = """
    あなたは医療情報の理解を支援するAIアシスタントです。
    医療用語や情報をわかりやすく説明し、一般の方の健康リテラシー向上をサポートします。
    
    以下のガイドラインに従ってください：
    
    1. 常に正確で最新の医療情報を提供するよう努める
    2. 専門用語を使う場合は、必ず平易な言葉で補足説明する
    3. あなたは診断や具体的な医療アドバイスを提供できない旨を適切に伝える
    4. 質問に答える際は、適切なツールを使用して情報を取得する
    5. 答えられない質問や専門的すぎる内容の場合は、専門家への相談を勧める
    6. 個人の症状や状態に基づく具体的なアドバイスは避け、一般的な情報提供に留める
    7. 不安を煽る表現や断定的な言い回しは避け、バランスの取れた情報を提供する
    8. 情報の限界や不確実性について適切に伝える
    9. Markdownを使って情報を整理して表示する（見出し、箇条書き、太字などを活用）
    10. 医療情報源や参考文献の重要性を伝え、信頼できる情報源を紹介する
    
    ユーザーが以下のような質問をした場合は、対応するツールを使用してください：
    - 医療用語に関する質問 → get_medical_term または search_medical_terms
    - 症状に関する質問 → get_symptom_info または search_symptoms
    - 治療法に関する質問 → get_treatment_info または search_treatments
    - 医療制度に関する質問 → get_healthcare_system_info または search_healthcare_systems
    - 予防医学に関する質問 → get_prevention_info
    - よくある質問 → get_faq
    
    必ず以下の免責事項を念頭に置いてください：
    このサービスは医療アドバイスや診断を提供するものではありません。具体的な症状や健康上の懸念がある場合は、
    医療専門家に相談することをお勧めします。提供される情報は一般的な教育目的であり、個人の医療判断の代わりにはなりません。
    """

    # 会話履歴がある場合は、それを含めてリクエストを作成
    messages = []
    previous_response_id = None

    if conversation_history:
        for msg in conversation_history:
            if msg["role"] == "user":
                messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "assistant" and "response_id" in msg:
                messages.append({"role": "assistant", "content": msg["content"]})
                previous_response_id = msg["response_id"]

    # 現在のユーザーメッセージを追加
    messages.append({"role": "user", "content": user_message})

    # OpenAI APIを呼び出し
    try:
        response = client.responses.create(
            model="gpt-4o",
            instructions=instructions,
            input=messages,
            tools=tools,
            tool_choice="auto",
            previous_response_id=previous_response_id,
        )

        # 関数呼び出しがある場合は処理
        function_calls = [msg for msg in response.output if msg.type == "function_call"]
        if function_calls:
            function_outputs = []
            for fc in function_calls:
                # 関数名とパラメータを取得
                func_name = fc.name
                params = json.loads(fc.arguments)

                # 対応する関数を呼び出し
                if func_name == "get_medical_term":
                    result = get_medical_term(**params)
                elif func_name == "search_medical_terms":
                    result = search_medical_terms(**params)
                elif func_name == "get_symptom_info":
                    result = get_symptom_info(**params)
                elif func_name == "search_symptoms":
                    result = search_symptoms(**params)
                elif func_name == "get_treatment_info":
                    result = get_treatment_info(**params)
                elif func_name == "search_treatments":
                    result = search_treatments(**params)
                elif func_name == "get_healthcare_system_info":
                    result = get_healthcare_system_info(**params)
                elif func_name == "search_healthcare_systems":
                    result = search_healthcare_systems(**params)
                elif func_name == "get_prevention_info":
                    result = get_prevention_info(**params)
                elif func_name == "get_faq":
                    result = get_faq(**params)
                else:
                    result = {"error": "未実装の関数です"}

                # 関数の出力を追加
                function_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": fc.call_id,
                        "output": json.dumps(result, ensure_ascii=False),
                    }
                )

            # ツール出力を含めて最終応答を生成
            final_response = client.responses.create(
                model="gpt-4o",
                instructions=instructions,
                input=function_outputs,
                previous_response_id=response.id,
            )

            return {
                "status": "success",
                "message": final_response.output_text,
                "response_id": final_response.id,
            }

        # 関数呼び出しがない場合は直接レスポンスを返す
        return {
            "status": "success",
            "message": response.output_text,
            "response_id": response.id,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"エラーが発生しました: {str(e)}",
        }


# --- コンソールインターフェース ---


def console_interface():
    """コンソールベースのチャットインターフェース"""
    api_key = setup_environment()
    client = openai.Client(api_key=api_key)
    conversation_history = []

    print("医療情報理解支援アシスタントへようこそ！")
    print(
        "医療用語や症状の説明、治療法の情報、医療制度の解説などについてお気軽にお問い合わせください。"
    )
    print("終了するには 'exit' と入力してください。\n")
    print(
        "免責事項: このサービスは医療アドバイスや診断を提供するものではありません。具体的な症状や健康上の懸念がある場合は、医療専門家に相談してください。\n"
    )

    while True:
        user_input = input("質問: ")
        if user_input.lower() in ["exit", "quit", "終了"]:
            print(
                "\nご利用ありがとうございました。また何かありましたらお気軽にお問い合わせください。"
            )
            break

        # ユーザーメッセージを会話履歴に追加
        conversation_history.append({"role": "user", "content": user_input})

        # チャットボットの応答を処理
        print("\n処理中...\n")
        response = process_chat(client, user_input, conversation_history)

        if response["status"] == "success":
            print(f"アシスタント: {response['message']}\n")
            # アシスタントの応答を会話履歴に追加
            conversation_history.append(
                {
                    "role": "assistant",
                    "content": response["message"],
                    "response_id": response.get("response_id"),
                }
            )
        else:
            print(f"エラー: {response['message']}\n")


# --- Webインターフェース ---

app = Flask(__name__)
api_client = None


@app.route("/")
def home():
    """ホームページを表示"""
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    """チャットAPIエンドポイント"""
    data = request.json
    user_message = data.get("message")
    conversation_history = data.get("history", [])

    if not user_message:
        return jsonify({"status": "error", "message": "メッセージが空です"})

    response = process_chat(api_client, user_message, conversation_history)
    return jsonify(response)


def web_interface():
    """Webベースのチャットインターフェース"""
    global api_client
    api_key = setup_environment()
    api_client = openai.Client(api_key=api_key)

    # テンプレートディレクトリの作成
    os.makedirs(os.path.join(os.path.dirname(__file__), "templates"), exist_ok=True)

    # HTMLテンプレートの作成（raw文字列を使用）
    html_template = r"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>医療情報理解支援アシスタント</title>
    <!-- Marked.js の読み込み -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f7fa;
            color: #333;
        }
        header {
            text-align: center;
            margin-bottom: 20px;
            padding: 10px;
            background-color: #3498db;
            color: white;
            border-radius: 8px;
        }
        .chat-container {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 20px;
            height: 500px;
            overflow-y: auto;
            margin-bottom: 20px;
            background-color: white;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .message {
            margin-bottom: 15px;
            padding: 10px 15px;
            border-radius: 18px;
            max-width: 80%;
            line-height: 1.5;
        }
        .user-message {
            background-color: #e3f2fd;
            margin-left: auto;
            text-align: right;
            color: #0056b3;
            border-bottom-right-radius: 5px;
        }
        .bot-message {
            background-color: #f0f4f8;
            margin-right: auto;
            border-bottom-left-radius: 5px;
        }
        .input-container {
            display: flex;
            gap: 10px;
        }
        #user-input {
            flex-grow: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 24px;
            font-size: 16px;
        }
        button {
            padding: 12px 20px;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 24px;
            cursor: pointer;
            font-weight: bold;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #2980b9;
        }
        .system-message {
            text-align: center;
            font-style: italic;
            color: #666;
            margin: 10px 0;
        }
        .loading {
            color: #999;
            font-style: italic;
        }
        footer {
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 0.8em;
        }
        .disclaimer {
            background-color: #fff8e1;
            padding: 10px 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 4px solid #ffc107;
        }
        .quick-links {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 20px 0;
        }
        .quick-link {
            background-color: #e3f2fd;
            border: 1px solid #3498db;
            color: #3498db;
            padding: 8px 15px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }
        .quick-link:hover {
            background-color: #3498db;
            color: white;
        }
    </style>
</head>
<body>
    <header>
        <h1>医療情報理解支援アシスタント</h1>
        <p>医療用語や症状の説明、治療法の情報などについてお気軽にお問い合わせください</p>
    </header>
    
    <div class="disclaimer">
        <p><strong>免責事項:</strong> このサービスは医療アドバイスや診断を提供するものではありません。具体的な症状や健康上の懸念がある場合は、医療専門家に相談してください。提供される情報は一般的な教育目的であり、個人の医療判断の代わりにはなりません。</p>
    </div>
    
    <div class="quick-links">
        <div class="quick-link" onclick="askQuestion('血糖値とは何ですか？')">血糖値について</div>
        <div class="quick-link" onclick="askQuestion('頭痛の種類について教えてください')">頭痛の種類</div>
        <div class="quick-link" onclick="askQuestion('MRIとCTスキャンの違いは？')">MRIとCTの違い</div>
        <div class="quick-link" onclick="askQuestion('健康保険の仕組みについて教えてください')">健康保険の仕組み</div>
        <div class="quick-link" onclick="askQuestion('生活習慣病の予防法について知りたいです')">生活習慣病予防</div>
    </div>
    
    <div class="chat-container" id="chat-container">
        <div class="message bot-message">
            こんにちは！医療情報理解支援アシスタントです。医療用語や症状の説明、治療法の情報などについてお気軽にお問い合わせください。医療専門家ではないため診断やアドバイスはできませんが、一般的な医療情報の理解をサポートします。
        </div>
    </div>
    
    <div class="input-container">
        <input type="text" id="user-input" placeholder="質問を入力してください...">
        <button id="send-button">送信</button>
    </div>
    
    <footer>
        <p>© 2025 医療情報理解支援アシスタント - このサービスはAIを活用して情報提供を行っています。</p>
        <p>緊急時や具体的な症状については必ず医療機関にご相談ください。</p>
    </footer>
    
    <script>
        const chatContainer = document.getElementById('chat-container');
        const userInput = document.getElementById('user-input');
        const sendButton = document.getElementById('send-button');
        
        // 会話履歴を保存
        let conversationHistory = [];
        
        function addMessage(message, isUser = false) {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message');
            messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');
            
            if (!isUser) {
                // Marked.js を利用してMarkdownをHTMLに変換
                messageDiv.innerHTML = marked.parse(message);
            } else {
                messageDiv.textContent = message;
            }
            
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            
            // 会話履歴に追加
            conversationHistory.push({
                role: isUser ? 'user' : 'assistant',
                content: message
            });
        }
        
        function addSystemMessage(message) {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('system-message');
            messageDiv.textContent = message;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        function addLoadingIndicator() {
            const loadingDiv = document.createElement('div');
            loadingDiv.classList.add('message', 'bot-message', 'loading');
            loadingDiv.textContent = '入力中...';
            loadingDiv.id = 'loading-indicator';
            chatContainer.appendChild(loadingDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            return loadingDiv;
        }
        
        function removeLoadingIndicator(indicator) {
            if (indicator && indicator.parentNode) {
                indicator.parentNode.removeChild(indicator);
            }
        }
        
        function askQuestion(question) {
            userInput.value = question;
            sendMessage();
        }
        
        async function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;
            
            // ユーザーメッセージを表示
            addMessage(message, true);
            userInput.value = '';
            
            // ローディングインジケータを表示
            const loadingIndicator = addLoadingIndicator();
            
            try {
                // APIリクエスト
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: message,
                        history: conversationHistory.slice(0, -1) // 最後のユーザーメッセージは除外
                    })
                });
                
                const data = await response.json();
                
                // ローディングインジケータを削除
                removeLoadingIndicator(loadingIndicator);
                
                if (data.status === 'success') {
                    // ボットの応答を表示
                    addMessage(data.message);
                    
                    // response_idがある場合は会話履歴に追加
                    if (data.response_id) {
                        conversationHistory[conversationHistory.length - 1].response_id = data.response_id;
                    }
                } else {
                    // エラーメッセージを表示
                    addSystemMessage('エラーが発生しました: ' + data.message);
                }
            } catch (error) {
                // ローディングインジケータを削除
                removeLoadingIndicator(loadingIndicator);
                
                // エラーメッセージを表示
                addSystemMessage('通信エラーが発生しました。再度お試しください。');
                console.error('Error:', error);
            }
        }
        
        // グローバルにaskQuestionを定義
        window.askQuestion = askQuestion;
        
        // 送信ボタンのクリックイベント
        sendButton.addEventListener('click', sendMessage);
        
        // Enterキーの押下イベント
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
    """

    # テンプレートを保存
    with open(
        os.path.join(os.path.dirname(__file__), "templates", "index.html"),
        "w",
        encoding="utf-8",
    ) as f:
        f.write(html_template)

    # Flaskアプリの起動
    print("Webインターフェースを起動しています...")
    print("以下のURLにアクセスしてください: http://localhost:5004")
    app.run(host="localhost", port=5004, debug=True)


def main():
    """メイン関数"""
    print("医療情報理解支援アシスタントのデモ\n")
    print("インターフェースを選択してください:")
    print("1: コンソールインターフェース（テキストベース）")
    print("2: Webインターフェース（ブラウザベース）")

    choice = input("\n選択してください (1 または 2): ").strip()

    if choice == "1":
        console_interface()
    elif choice == "2":
        web_interface()
    else:
        print("無効な選択です。デフォルトのコンソールインターフェースを起動します。")
        console_interface()


if __name__ == "__main__":
    main()
