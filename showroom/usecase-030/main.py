"""
カスタマーサポートチャットボット

このサンプルは、OpenAI Responses APIを使用したカスタマーサポートチャットボットを実装しています。
商品情報、注文状況、FAQなどの情報を取得するための関数を定義し、
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

# 商品データを読み込み
from product_data import (
    get_product_info,
    search_products,
    get_faq,
    get_policy,
    get_order_status,
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

class ProductInfoRequest(BaseModel):
    """商品情報取得のリクエストモデル"""
    product_id: str = Field(..., description="商品ID（例: TS-100）")


class SearchProductsRequest(BaseModel):
    """商品検索のリクエストモデル"""
    query: str = Field(..., description="検索キーワード")
    category: Optional[str] = Field(None, description="商品カテゴリ（指定しない場合は全カテゴリから検索）")


class FaqRequest(BaseModel):
    """FAQ検索のリクエストモデル"""
    query: Optional[str] = Field(None, description="検索キーワード（指定しない場合は全FAQを取得）")


class PolicyRequest(BaseModel):
    """ポリシー情報取得のリクエストモデル"""
    policy_type: str = Field(..., description="ポリシータイプ（shipping, returns, warranty, privacy）")


class OrderStatusRequest(BaseModel):
    """注文状況取得のリクエストモデル"""
    order_id: str = Field(..., description="注文ID（例: ORD-12345）")


# --- ツール定義 ---

def setup_tools():
    """ツール定義を設定します。"""
    return [
        {
            "type": "function",
            "name": "get_product_info",
            "description": "商品IDを指定して商品の詳細情報を取得します",
            "parameters": ProductInfoRequest.schema(),
        },
        {
            "type": "function",
            "name": "search_products",
            "description": "キーワードで商品を検索します",
            "parameters": SearchProductsRequest.schema(),
        },
        {
            "type": "function",
            "name": "get_faq",
            "description": "よくある質問（FAQ）を検索します",
            "parameters": FaqRequest.schema(),
        },
        {
            "type": "function",
            "name": "get_policy",
            "description": "会社のポリシー情報を取得します",
            "parameters": PolicyRequest.schema(),
        },
        {
            "type": "function",
            "name": "get_order_status",
            "description": "注文IDを指定して注文状況を確認します",
            "parameters": OrderStatusRequest.schema(),
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
    あなたは家電製品を販売するオンラインショップのカスタマーサポートアシスタントです。
    親切、丁寧、プロフェッショナルな対応を心がけ、必要に応じて提供されたツールを使用して
    お客様のお問い合わせに回答してください。
    
    以下のガイドラインに従ってください：
    1. 常に礼儀正しく、敬語を使って対応する
    2. 質問に対しては具体的かつ簡潔に回答する
    3. 商品や注文に関する質問には、必ずツールを使用して正確な情報を提供する
    4. わからないことや情報がない場合は、誤った情報を提供せず、正直に伝える
    5. 複雑な問題については、カスタマーサポート窓口への連絡を案内する
    6. 個人情報やセキュリティに関する事項は慎重に扱う
    
    お客様が以下のような質問をした場合は、対応するツールを使用してください：
    - 商品に関する質問 → get_product_info または search_products
    - 注文や配送に関する質問 → get_order_status
    - 返品や保証に関する質問 → get_policy
    - よくある質問 → get_faq
    """
    
    # 会話履歴がある場合は、それを含めてリクエストを作成
    input_messages = []
    previous_response_id = None
    
    if conversation_history:
        for msg in conversation_history:
            if msg["role"] == "user":
                input_messages.append({"type": "text", "text": msg["content"]})
            elif msg["role"] == "assistant" and "response_id" in msg:
                previous_response_id = msg["response_id"]
    
    # 現在のユーザーメッセージを追加
    input_messages.append({"type": "text", "text": user_message})
    
    # OpenAI APIを呼び出し
    try:
        response = client.responses.create(
            model="gpt-4o",
            instructions=instructions,
            input=input_messages if len(input_messages) > 1 else input_messages[0]["text"],
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
                if func_name == "get_product_info":
                    result = get_product_info(**params)
                elif func_name == "search_products":
                    result = search_products(**params)
                elif func_name == "get_faq":
                    result = get_faq(**params)
                elif func_name == "get_policy":
                    result = get_policy(**params)
                elif func_name == "get_order_status":
                    result = get_order_status(**params)
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
    
    print("家電製品カスタマーサポートチャットボットへようこそ！")
    print("ご質問や商品に関するお問い合わせをどうぞ。終了するには 'exit' と入力してください。\n")
    
    while True:
        user_input = input("お客様: ")
        if user_input.lower() in ["exit", "quit", "終了"]:
            print("\nご利用ありがとうございました。またのお問い合わせをお待ちしております。")
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
        <title>カスタマーサポートチャット</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            .chat-container {
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 20px;
                height: 500px;
                overflow-y: auto;
                margin-bottom: 20px;
                background-color: #f9f9f9;
            }
            .message {
                margin-bottom: 15px;
                padding: 10px;
                border-radius: 8px;
                max-width: 80%;
            }
            .user-message {
                background-color: #e3f2fd;
                margin-left: auto;
                text-align: right;
            }
            .bot-message {
                background-color: #f0f0f0;
                margin-right: auto;
            }
            .input-container {
                display: flex;
                gap: 10px;
            }
            #user-input {
                flex-grow: 1;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            button {
                padding: 10px 20px;
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            button:hover {
                background-color: #45a049;
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
        </style>
    </head>
    <body>
        <h1>カスタマーサポートチャット</h1>
        <p>商品情報、注文状況、返品ポリシーなどについてお気軽にお問い合わせください。</p>
        
        <div class="chat-container" id="chat-container">
            <div class="message bot-message">
                こんにちは！家電製品オンラインショップのカスタマーサポートです。どのようなご質問がありますか？
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="user-input" placeholder="メッセージを入力してください...">
            <button id="send-button">送信</button>
        </div>
        
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
    print("カスタマーサポートチャットボットのデモ\n")
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