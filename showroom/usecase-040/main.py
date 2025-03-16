"""
市民向け行政サービス案内

このサンプルは、OpenAI Responses APIを使用した市民向け行政サービス案内チャットボットを実装しています。
行政手続き情報、施設情報、イベント情報、FAQなどを取得するための関数を定義し、
ユーザーからの問い合わせに対して適切な応答を生成します。
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

# 行政サービスデータを管理するモジュール
from government_data import (
    get_procedure_info,
    search_procedures,
    get_facility_info,
    search_facilities,
    get_event_info,
    search_events,
    get_faq,
    get_emergency_info
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

class ProcedureInfoRequest(BaseModel):
    """行政手続き情報取得のリクエストモデル"""
    procedure_id: str = Field(..., description="手続きID（例: CERT-001）")


class SearchProceduresRequest(BaseModel):
    """行政手続き検索のリクエストモデル"""
    query: str = Field(..., description="検索キーワード")
    category: Optional[str] = Field(None, description="手続きカテゴリ（residence:住民関連, tax:税金関連, welfare:福祉関連）")


class FacilityInfoRequest(BaseModel):
    """施設情報取得のリクエストモデル"""
    facility_id: str = Field(..., description="施設ID（例: LIB-001）")


class SearchFacilitiesRequest(BaseModel):
    """施設検索のリクエストモデル"""
    query: str = Field(..., description="検索キーワード")
    facility_type: Optional[str] = Field(None, description="施設タイプ（library:図書館, community:公民館, sports:スポーツ施設, government:行政施設）")


class EventInfoRequest(BaseModel):
    """イベント情報取得のリクエストモデル"""
    event_id: str = Field(..., description="イベントID（例: EVENT-001）")


class SearchEventsRequest(BaseModel):
    """イベント検索のリクエストモデル"""
    query: Optional[str] = Field(None, description="検索キーワード")
    date_from: Optional[str] = Field(None, description="開始日（YYYY-MM-DD形式）")
    date_to: Optional[str] = Field(None, description="終了日（YYYY-MM-DD形式）")
    event_type: Optional[str] = Field(None, description="イベントタイプ（seminar:セミナー, festival:お祭り, consultation:相談会, workshop:ワークショップ）")


class FaqRequest(BaseModel):
    """FAQ検索のリクエストモデル"""
    query: Optional[str] = Field(None, description="検索キーワード（指定しない場合は全FAQを取得）")
    category: Optional[str] = Field(None, description="カテゴリ（garbage:ゴミ, tax:税金, childcare:子育て, elderly:高齢者, disaster:防災）")


class EmergencyInfoRequest(BaseModel):
    """緊急情報取得のリクエストモデル"""
    info_type: Optional[str] = Field(None, description="情報タイプ（disaster:災害情報, weather:気象情報, health:健康・感染症情報）")


# --- ツール定義 ---

def setup_tools():
    """ツール定義を設定します。"""
    return [
        {
            "type": "function",
            "name": "get_procedure_info",
            "description": "行政手続きIDを指定して手続きの詳細情報を取得します",
            "parameters": {
                "type": "object",
                "properties": {
                    "procedure_id": {
                        "type": "string",
                        "description": "手続きID（例: CERT-001）"
                    }
                },
                "required": ["procedure_id"]
            }
        },
        {
            "type": "function",
            "name": "search_procedures",
            "description": "キーワードで行政手続きを検索します",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "検索キーワード"
                    },
                    "category": {
                        "type": "string",
                        "description": "手続きカテゴリ（residence:住民関連, tax:税金関連, welfare:福祉関連）"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "type": "function",
            "name": "get_facility_info",
            "description": "施設IDを指定して施設の詳細情報を取得します",
            "parameters": {
                "type": "object",
                "properties": {
                    "facility_id": {
                        "type": "string",
                        "description": "施設ID（例: LIB-001）"
                    }
                },
                "required": ["facility_id"]
            }
        },
        {
            "type": "function",
            "name": "search_facilities",
            "description": "キーワードで施設を検索します",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "検索キーワード"
                    },
                    "facility_type": {
                        "type": "string",
                        "description": "施設タイプ（library:図書館, community:公民館, sports:スポーツ施設, government:行政施設）"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "type": "function",
            "name": "get_event_info",
            "description": "イベントIDを指定してイベントの詳細情報を取得します",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "string",
                        "description": "イベントID（例: EVENT-001）"
                    }
                },
                "required": ["event_id"]
            }
        },
        {
            "type": "function",
            "name": "search_events",
            "description": "条件を指定してイベントを検索します",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "検索キーワード"
                    },
                    "date_from": {
                        "type": "string",
                        "description": "開始日（YYYY-MM-DD形式）"
                    },
                    "date_to": {
                        "type": "string",
                        "description": "終了日（YYYY-MM-DD形式）"
                    },
                    "event_type": {
                        "type": "string",
                        "description": "イベントタイプ（seminar:セミナー, festival:お祭り, consultation:相談会, workshop:ワークショップ）"
                    }
                }
            }
        },
        {
            "type": "function",
            "name": "get_faq",
            "description": "行政サービスに関するよくある質問（FAQ）を検索します",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "検索キーワード"
                    },
                    "category": {
                        "type": "string",
                        "description": "カテゴリ（garbage:ゴミ, tax:税金, childcare:子育て, elderly:高齢者, disaster:防災）"
                    }
                }
            }
        },
        {
            "type": "function",
            "name": "get_emergency_info",
            "description": "現在の緊急情報を取得します",
            "parameters": {
                "type": "object",
                "properties": {
                    "info_type": {
                        "type": "string",
                        "description": "情報タイプ（disaster:災害情報, weather:気象情報, health:健康・感染症情報）"
                    }
                }
            }
        }
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
    あなたは地方自治体の行政サービス案内AIアシスタントです。
    市民からの行政手続き、公共施設、イベント、その他行政サービスに関する
    問い合わせに丁寧に回答してください。必要に応じて提供されたツールを使用して
    最新の正確な情報を提供してください。

    以下のガイドラインに従ってください：
    1. 常に礼儀正しく、敬語を使って対応する
    2. 質問に対しては具体的かつ簡潔に回答する
    3. 行政手続きや施設に関する質問には、必ずツールを使用して正確な情報を提供する
    4. わからないことや情報がない場合は、誤った情報を提供せず、正直に伝える
    5. 個人の状況によって異なる可能性がある場合は、一般的な情報を提供し、詳細は窓口での相談を案内する
    6. 行政サービスの利用方法についてはできるだけ具体的に説明し、必要書類や手続き方法を案内する
    7. 緊急の相談（災害、生活困窮など）については、適切な窓口や連絡先を案内する
    
    市民が以下のような質問をした場合は、対応するツールを使用してください：
    - 行政手続きに関する質問 → get_procedure_info または search_procedures
    - 公共施設に関する質問 → get_facility_info または search_facilities
    - イベントに関する質問 → get_event_info または search_events
    - よくある質問 → get_faq
    - 緊急情報 → get_emergency_info
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
                if func_name == "get_procedure_info":
                    result = get_procedure_info(**params)
                elif func_name == "search_procedures":
                    result = search_procedures(**params)
                elif func_name == "get_facility_info":
                    result = get_facility_info(**params)
                elif func_name == "search_facilities":
                    result = search_facilities(**params)
                elif func_name == "get_event_info":
                    result = get_event_info(**params)
                elif func_name == "search_events":
                    result = search_events(**params)
                elif func_name == "get_faq":
                    result = get_faq(**params)
                elif func_name == "get_emergency_info":
                    result = get_emergency_info(**params)
                else:
                    result = {"error": "未実装の関数です"}
                
                # 関数の出力を追加
                function_outputs.append({
                    "type": "function_call_output",
                    "call_id": fc.call_id,
                    "output": json.dumps(result, ensure_ascii=False),
                })
            
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
    
    print("市民向け行政サービス案内AIアシスタントへようこそ！")
    print("行政手続き、施設情報、イベント情報などについてお気軽にお問い合わせください。")
    print("終了するには 'exit' と入力してください。\n")
    
    while True:
        user_input = input("市民: ")
        if user_input.lower() in ["exit", "quit", "終了"]:
            print("\nご利用ありがとうございました。また何かありましたらお気軽にお問い合わせください。")
            break
        
        # ユーザーメッセージを会話履歴に追加
        conversation_history.append({"role": "user", "content": user_input})
        
        # チャットボットの応答を処理
        print("\n処理中...\n")
        response = process_chat(client, user_input, conversation_history)
        
        if response["status"] == "success":
            print(f"アシスタント: {response['message']}\n")
            # アシスタントの応答を会話履歴に追加
            conversation_history.append({
                "role": "assistant",
                "content": response["message"],
                "response_id": response.get("response_id")
            })
        else:
            print(f"エラー: {response['message']}\n")


# --- Webインターフェース ---

app = Flask(__name__)
api_client = None


@app.route('/')
def home():
    """ホームページを表示"""
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """チャットAPIエンドポイント"""
    data = request.json
    user_message = data.get('message')
    conversation_history = data.get('history', [])
    
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
    os.makedirs(os.path.join(os.path.dirname(__file__), 'templates'), exist_ok=True)
    
    # HTMLテンプレートの作成
    html_template = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>市民向け行政サービス案内</title>
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
                background-color: #0056b3;
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
                background-color: #0056b3;
                color: white;
                border: none;
                border-radius: 24px;
                cursor: pointer;
                font-weight: bold;
                transition: background-color 0.3s;
            }
            button:hover {
                background-color: #003d82;
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
            .quick-links {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin: 20px 0;
            }
            .quick-link {
                background-color: #e3f2fd;
                border: 1px solid #0056b3;
                color: #0056b3;
                padding: 8px 15px;
                border-radius: 20px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.3s;
            }
            .quick-link:hover {
                background-color: #0056b3;
                color: white;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>市民向け行政サービス案内</h1>
            <p>行政手続き、施設情報、イベント情報などについてお気軽にお問い合わせください</p>
        </header>
        
        <div class="quick-links">
            <div class="quick-link" onclick="askQuestion('住民票の取得方法について教えてください')">住民票について</div>
            <div class="quick-link" onclick="askQuestion('ゴミの分別方法について知りたいです')">ゴミの分別</div>
            <div class="quick-link" onclick="askQuestion('市内の図書館はどこにありますか？')">図書館情報</div>
            <div class="quick-link" onclick="askQuestion('今週末のイベントはありますか？')">イベント情報</div>
            <div class="quick-link" onclick="askQuestion('市役所の開庁時間を教えてください')">市役所情報</div>
        </div>
        
        <div class="chat-container" id="chat-container">
            <div class="message bot-message">
                こんにちは！市民向け行政サービス案内AIアシスタントです。行政手続き、施設情報、イベント情報などについてお気軽にお問い合わせください。
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="user-input" placeholder="質問を入力してください...">
            <button id="send-button">送信</button>
        </div>
        
        <footer>
            <p>© 2025 市民向け行政サービス案内 - このサービスはAIを活用して情報提供を行っています。</p>
            <p>緊急時は各担当窓口に直接お問い合わせください。</p>
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
                messageDiv.textContent = message;
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
    with open(os.path.join(os.path.dirname(__file__), 'templates', 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    # Flaskアプリの起動
    print("Webインターフェースを起動しています...")
    print("以下のURLにアクセスしてください: http://localhost:5000")
    app.run(debug=True)


def main():
    """メイン関数"""
    print("市民向け行政サービス案内AIアシスタントのデモ\n")
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