"""
法的文書のレビューと要約: OpenAI APIを使用して法的文書の分析と要約を行うWebアプリケーション
"""
import os
import io
import tempfile
import base64
from datetime import datetime
import json
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import PyPDF2
from openai import OpenAI
import markdown
import pdfkit
from colorama import Fore, Style
from bs4 import BeautifulSoup

# 環境変数の読み込み
load_dotenv()

# Flaskアプリの初期化
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB制限
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# OpenAI APIクライアントの初期化
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 許可されるファイル拡張子
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}

def allowed_file(filename):
    """ファイル拡張子が許可されているかチェック"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """PDFファイルからテキストを抽出"""
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text

def chunk_text(text, max_tokens=8000):
    """テキストを適切なサイズのチャンクに分割"""
    # 簡易的なトークン推定: 英単語は平均4文字で1トークン程度
    words = text.split()
    chunks = []
    current_chunk = []
    current_token_count = 0
    
    for word in words:
        # 単語のトークン数を単純に推定（単語の文字数/4）
        word_token_count = len(word) // 4 + 1
        
        if current_token_count + word_token_count > max_tokens:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_token_count = word_token_count
        else:
            current_chunk.append(word)
            current_token_count += word_token_count
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def analyze_document(text, analysis_type):
    """文書の分析を実行"""
    # 文書が長い場合はチャンクに分割
    chunks = chunk_text(text)
    
    results = {}
    
    # ドキュメントの種類を特定
    doc_type_response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "あなたは法律文書の分析を専門とする法律アシスタントです。ユーザーが提供する文書の種類を特定してください。"},
            {"role": "user", "content": f"以下の法的文書の種類を特定してください。契約書、利用規約、プライバシーポリシー、法律文書、その他のいずれかで分類し、理由も説明してください。\n\n{chunks[0][:2000]}"}
        ]
    )
    document_type = doc_type_response.choices[0].message.content
    results["document_type"] = document_type
    
    # 分析タイプに応じた処理
    if analysis_type == "summary" or analysis_type == "all":
        summary_response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "あなたは法律文書の分析を専門とする法律アシスタントです。与えられた法的文書の要約を500-800字程度で作成してください。"},
                {"role": "user", "content": f"以下の法的文書の要約を作成してください：\n\n{chunks[0]}"}
            ]
        )
        results["summary"] = summary_response.choices[0].message.content
    
    if analysis_type == "key_points" or analysis_type == "all":
        key_points_response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "あなたは法律文書の分析を専門とする法律アシスタントです。与えられた法的文書から重要なポイントを箇条書きで抽出してください。各ポイントには文書内の対応するセクションや条項番号も示してください。"},
                {"role": "user", "content": f"以下の法的文書から重要なポイントを10-15個抽出し、箇条書きで提示してください：\n\n{chunks[0]}"}
            ]
        )
        results["key_points"] = key_points_response.choices[0].message.content
    
    if analysis_type == "risks" or analysis_type == "all":
        risks_response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "あなたは法律文書の分析を専門とする法律アシスタントです。与えられた法的文書から潜在的な法的リスクを特定し、それぞれのリスクレベル（高・中・低）を評価してください。"},
                {"role": "user", "content": f"以下の法的文書から潜在的な法的リスクを特定し、リスクレベル（高・中・低）と共に説明してください：\n\n{chunks[0]}"}
            ]
        )
        results["risks"] = risks_response.choices[0].message.content
    
    if analysis_type == "terminology" or analysis_type == "all":
        terminology_response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "あなたは法律文書の分析を専門とする法律アシスタントです。与えられた法的文書から専門的な法律用語を抽出し、それらを平易な言葉で説明してください。"},
                {"role": "user", "content": f"以下の法的文書から専門的な法律用語を8-12個抽出し、それぞれを平易な言葉で説明してください：\n\n{chunks[0]}"}
            ]
        )
        results["terminology"] = terminology_response.choices[0].message.content
    
    if analysis_type == "structure" or analysis_type == "all":
        structure_response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "あなたは法律文書の分析を専門とする法律アシスタントです。与えられた法的文書の構造を分析し、主要なセクションとその目的を説明してください。"},
                {"role": "user", "content": f"以下の法的文書の構造を分析し、主要なセクションとその目的を説明してください：\n\n{chunks[0]}"}
            ]
        )
        results["structure"] = structure_response.choices[0].message.content
    
    return results

def generate_report(analysis_results, file_name, text_content):
    """分析結果からHTMLレポートを生成"""
    # マークダウンレポートを作成
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    markdown_content = f"""# 法的文書分析レポート

**分析日時**: {now}  
**ファイル名**: {file_name}  
**文書タイプ**: {analysis_results.get('document_type', 'N/A')}

## 要約

{analysis_results.get('summary', 'この分析は実行されませんでした。')}

## 重要なポイント

{analysis_results.get('key_points', 'この分析は実行されませんでした。')}

## 潜在的リスク

{analysis_results.get('risks', 'この分析は実行されませんでした。')}

## 法律用語の説明

{analysis_results.get('terminology', 'この分析は実行されませんでした。')}

## 文書構造

{analysis_results.get('structure', 'この分析は実行されませんでした。')}

---

*免責事項: この分析は自動的に生成されたものであり、法的アドバイスを構成するものではありません。重要な法的判断には、必ず弁護士にご相談ください。*
"""
    
    # マークダウンをHTMLに変換
    html_content = markdown.markdown(markdown_content)
    
    # HTMLテンプレートを読み込む
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'report_template.html')
    
    # テンプレートがなければ作成
    if not os.path.exists(template_path):
        os.makedirs(os.path.dirname(template_path), exist_ok=True)
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write("""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>法的文書分析レポート</title>
    <style>
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            line-height: it.6;
            color: #333;
            max-width: 900px;
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
        .disclaimer {
            background-color: #f8f9fa;
            border-left: 4px solid #e74c3c;
            padding: 15px;
            margin-top: 40px;
        }
        .info-row {
            margin-bottom: 5px;
        }
        .risk-high {
            color: #e74c3c;
            font-weight: bold;
        }
        .risk-medium {
            color: #f39c12;
            font-weight: bold;
        }
        .risk-low {
            color: #27ae60;
            font-weight: bold;
        }
        .term {
            font-weight: bold;
            color: #2980b9;
        }
        .term-definition {
            margin-left: 20px;
            margin-bottom: 15px;
        }
        pre {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="content">
        {{content}}
    </div>
</body>
</html>""")
    
    # テンプレートを読み込み、内容を置換
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # HTMLコンテンツを整形
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # リスク表示のカラーコーディング適用
    for p in soup.find_all('p'):
        text = p.get_text()
        if '高リスク' in text or 'リスク: 高' in text:
            p['class'] = p.get('class', []) + ['risk-high']
        elif '中リスク' in text or 'リスク: 中' in text:
            p['class'] = p.get('class', []) + ['risk-medium']
        elif '低リスク' in text or 'リスク: 低' in text:
            p['class'] = p.get('class', []) + ['risk-low']
    
    # 用語の強調
    for li in soup.find_all('li'):
        text = li.get_text()
        if ':' in text or '：' in text:
            term, definition = text.split(':', 1) if ':' in text else text.split('：', 1)
            new_li = soup.new_tag('div')
            term_span = soup.new_tag('div')
            term_span['class'] = 'term'
            term_span.string = term.strip()
            def_span = soup.new_tag('div')
            def_span['class'] = 'term-definition'
            def_span.string = definition.strip()
            new_li.append(term_span)
            new_li.append(def_span)
            li.replace_with(new_li)
    
    formatted_html = template.replace("{{content}}", str(soup))
    
    return formatted_html

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'document' not in request.files:
        return jsonify({'error': 'ファイルがありません'}), 400
    
    file = request.files['document']
    analysis_type = request.form.get('analysisType', 'all')
    
    if file.filename == '':
        return jsonify({'error': 'ファイルが選択されていません'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # PDFからテキスト抽出
            if filename.endswith('.pdf'):
                text_content = extract_text_from_pdf(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
            
            # テキストが少なすぎる場合はエラー
            if len(text_content) < 100:
                return jsonify({'error': 'テキストが抽出できないか、内容が少なすぎます。別の文書を試してください。'}), 400
            
            # 文書分析
            print(f"{Fore.GREEN}文書「{filename}」の分析を開始します...{Style.RESET_ALL}")
            analysis_results = analyze_document(text_content, analysis_type)
            
            # HTMLレポート生成
            html_report = generate_report(analysis_results, filename, text_content)
            
            # 一時ファイルにHTMLレポートを保存
            report_filename = f"legal_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            report_path = os.path.join(app.config['UPLOAD_FOLDER'], report_filename)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_report)
            
            # PDFレポートの生成（オプション）
            pdf_path = None
            try:
                pdf_path = report_path.replace('.html', '.pdf')
                pdfkit.from_string(html_report, pdf_path)
                have_pdf = True
            except Exception as e:
                print(f"PDF生成エラー: {str(e)}")
                have_pdf = False
            
            # 結果を返す
            return jsonify({
                'success': True,
                'document_type': analysis_results.get('document_type', '不明'),
                'summary': analysis_results.get('summary', ''),
                'key_points': analysis_results.get('key_points', ''),
                'risks': analysis_results.get('risks', ''),
                'terminology': analysis_results.get('terminology', ''),
                'structure': analysis_results.get('structure', ''),
                'report_path': report_filename,
                'have_pdf': have_pdf,
                'pdf_path': os.path.basename(pdf_path) if have_pdf else None
            })
            
        except Exception as e:
            print(f"エラー発生: {str(e)}")
            return jsonify({'error': f'分析中にエラーが発生しました: {str(e)}'}), 500
        
    return jsonify({'error': '許可されていないファイル形式です'}), 400

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

@app.route('/viewreport/<filename>')
def view_report(filename):
    try:
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"レポートの表示中にエラーが発生しました: {str(e)}", 500

def create_template_files():
    """テンプレートファイルを作成"""
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    # index.htmlテンプレート
    index_path = os.path.join(template_dir, 'index.html')
    if not os.path.exists(index_path):
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>法的文書分析ツール</title>
    <style>
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1000px;
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
        .card {
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 20px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="file"] {
            display: block;
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #2980b9;
        }
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
        .spinner {
            border: 4px solid rgba(0, 0, 0, 0.1);
            width: 36px;
            height: 36px;
            border-radius: 50%;
            border-left-color: #3498db;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        .result {
            display: none;
            margin-top: 30px;
        }
        .tab {
            overflow: hidden;
            border: 1px solid #ccc;
            background-color: #f1f1f1;
            border-radius: 4px 4px 0 0;
        }
        .tab button {
            background-color: inherit;
            float: left;
            border: none;
            outline: none;
            cursor: pointer;
            padding: 14px 16px;
            transition: 0.3s;
            color: #333;
        }
        .tab button:hover {
            background-color: #ddd;
        }
        .tab button.active {
            background-color: #3498db;
            color: white;
        }
        .tabcontent {
            display: none;
            padding: 20px;
            border: 1px solid #ccc;
            border-top: none;
            border-radius: 0 0 4px 4px;
        }
        .download-btn {
            display: inline-block;
            background-color: #27ae60;
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 4px;
            margin-top: 20px;
        }
        .download-btn:hover {
            background-color: #2ecc71;
        }
        pre {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            white-space: pre-wrap;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .error {
            color: #e74c3c;
            font-weight: bold;
            padding: 10px;
            background-color: #fadbd8;
            border-radius: 4px;
            margin: 20px 0;
        }
        .disclaimer {
            font-size: 12px;
            margin-top: 40px;
            padding: 10px;
            background-color: #f8f9fa;
            border-left: 4px solid #e74c3c;
        }
    </style>
</head>
<body>
    <h1>法的文書分析ツール</h1>
    <p>PDF形式の法的文書をアップロードして、OpenAI APIを使用した分析結果を確認できます。</p>

    <div class="card">
        <h2>文書アップロード</h2>
        <form id="uploadForm">
            <div class="form-group">
                <label for="document">法的文書 (PDF、TXT)</label>
                <input type="file" id="document" name="document" accept=".pdf,.txt,.docx" required>
            </div>
            <div class="form-group">
                <label for="analysisType">分析タイプ</label>
                <select id="analysisType" name="analysisType">
                    <option value="all">すべて分析</option>
                    <option value="summary">要約のみ</option>
                    <option value="key_points">重要ポイントのみ</option>
                    <option value="risks">リスク分析のみ</option>
                    <option value="terminology">用語説明のみ</option>
                    <option value="structure">文書構造のみ</option>
                </select>
            </div>
            <button type="submit">分析開始</button>
        </form>
        
        <div class="loading">
            <div class="spinner"></div>
            <p>文書を分析しています。しばらくお待ちください...</p>
        </div>
        
        <div id="error" class="error" style="display: none;"></div>
    </div>

    <div id="result" class="result">
        <h2>分析結果: <span id="docTitle"></span></h2>
        <p>文書タイプ: <span id="docType"></span></p>
        
        <div class="tab">
            <button class="tablinks active" onclick="openTab(event, 'summary')">要約</button>
            <button class="tablinks" onclick="openTab(event, 'keyPoints')">重要ポイント</button>
            <button class="tablinks" onclick="openTab(event, 'risks')">リスク分析</button>
            <button class="tablinks" onclick="openTab(event, 'terminology')">用語説明</button>
            <button class="tablinks" onclick="openTab(event, 'structure')">文書構造</button>
        </div>
        
        <div id="summary" class="tabcontent" style="display: block;">
            <pre id="summaryContent"></pre>
        </div>
        
        <div id="keyPoints" class="tabcontent">
            <pre id="keyPointsContent"></pre>
        </div>
        
        <div id="risks" class="tabcontent">
            <pre id="risksContent"></pre>
        </div>
        
        <div id="terminology" class="tabcontent">
            <pre id="terminologyContent"></pre>
        </div>
        
        <div id="structure" class="tabcontent">
            <pre id="structureContent"></pre>
        </div>
        
        <div class="download-options">
            <a id="htmlReport" class="download-btn" target="_blank">HTML形式で表示</a>
            <a id="pdfReport" class="download-btn" style="display: none;">PDF形式でダウンロード</a>
        </div>
    </div>

    <div class="disclaimer">
        <p><strong>免責事項:</strong> この分析は自動的に生成されたものであり、法的アドバイスを構成するものではありません。重要な法的判断には、必ず弁護士にご相談ください。</p>
    </div>

    <script>
        document.getElementById('uploadForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const fileInput = document.getElementById('document');
            const analysisType = document.getElementById('analysisType').value;
            
            // ファイル検証
            if (!fileInput.files.length) {
                showError('ファイルを選択してください');
                return;
            }
            
            const file = fileInput.files[0];
            const allowedTypes = ['application/pdf', 'text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
            if (!allowedTypes.includes(file.type)) {
                showError('PDF、TXT、DOCXファイルのみ許可されています');
                return;
            }
            
            // フォームデータ準備
            const formData = new FormData();
            formData.append('document', file);
            formData.append('analysisType', analysisType);
            
            // UI更新
            document.querySelector('.loading').style.display = 'block';
            document.getElementById('error').style.display = 'none';
            document.getElementById('result').style.display = 'none';
            
            // APIリクエスト
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                document.querySelector('.loading').style.display = 'none';
                
                if (data.error) {
                    showError(data.error);
                    return;
                }
                
                // 結果表示
                document.getElementById('docTitle').textContent = file.name;
                document.getElementById('docType').textContent = data.document_type;
                
                document.getElementById('summaryContent').textContent = data.summary || '要約は生成されませんでした。';
                document.getElementById('keyPointsContent').textContent = data.key_points || '重要ポイントは抽出されませんでした。';
                document.getElementById('risksContent').textContent = data.risks || 'リスク分析は実行されませんでした。';
                document.getElementById('terminologyContent').textContent = data.terminology || '用語説明は生成されませんでした。';
                document.getElementById('structureContent').textContent = data.structure || '文書構造の分析は実行されませんでした。';
                
                // レポートリンク
                document.getElementById('htmlReport').href = '/viewreport/' + data.report_path;
                
                if (data.have_pdf) {
                    document.getElementById('pdfReport').style.display = 'inline-block';
                    document.getElementById('pdfReport').href = '/download/' + data.pdf_path;
                } else {
                    document.getElementById('pdfReport').style.display = 'none';
                }
                
                document.getElementById('result').style.display = 'block';
            })
            .catch(error => {
                document.querySelector('.loading').style.display = 'none';
                showError('エラーが発生しました: ' + error.message);
            });
        });
        
        function showError(message) {
            const errorElement = document.getElementById('error');
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }
        
        function openTab(evt, tabName) {
            // タブコンテンツを非表示
            const tabcontents = document.getElementsByClassName('tabcontent');
            for (let i = 0; i < tabcontents.length; i++) {
                tabcontents[i].style.display = 'none';
            }
            
            // タブボタンからアクティブクラスを削除
            const tablinks = document.getElementsByClassName('tablinks');
            for (let i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(' active', '');
            }
            
            // 選択したタブを表示してアクティブにする
            document.getElementById(tabName).style.display = 'block';
            evt.currentTarget.className += ' active';
        }
    </script>
</body>
</html>""")
    
    # サンプル文書の作成
    samples_dir = os.path.join(os.path.dirname(__file__), 'sample_documents')
    os.makedirs(samples_dir, exist_ok=True)
    
    # サンプル契約書
    sample_contract_path = os.path.join(samples_dir, 'sample_contract.txt')
    if not os.path.exists(sample_contract_path):
        with open(sample_contract_path, 'w', encoding='utf-8') as f:
            f.write("""業務委託契約書

株式会社ABC（以下「甲」という）と株式会社XYZ（以下「乙」という）は、以下のとおり業務委託契約（以下「本契約」という）を締結する。

第1条（目的）
本契約は、甲が乙に対し、第2条に定める業務を委託し、乙がこれを受託することについて、必要な事項を定めることを目的とする。

第2条（委託業務）
甲が乙に委託する業務（以下「委託業務」という）の内容は、以下のとおりとする。
(1) Webサイトのデザイン制作業務
(2) コンテンツの企画および制作業務
(3) システム開発および保守業務
(4) 前各号に付随する業務

第3条（委託料および支払方法）
1. 甲は、乙に対し、委託業務の対価として、月額金1,000,000円（消費税別）を支払うものとする。
2. 乙は、毎月末日に、前項に定める委託料の請求書を甲に送付する。
3. 甲は、前項の請求書を受領した日の翌月末日までに、乙の指定する銀行口座に委託料を振り込む方法により支払うものとする。振込手数料は甲の負担とする。

第4条（契約期間）
1. 本契約の有効期間は、20XX年4月1日から1年間とする。
2. 前項の定めにかかわらず、期間満了の3ヶ月前までに、甲または乙のいずれからも書面による別段の意思表示がないときは、本契約は同一条件でさらに1年間更新されるものとし、以後も同様とする。

第5条（機密保持）
1. 甲および乙は、本契約の履行に関連して知り得た相手方の技術上、営業上その他一切の情報（以下「機密情報」という）を、相手方の事前の書面による承諾なく第三者に開示または漏洩してはならず、また、本契約の履行以外の目的に使用してはならない。
2. 前項の定めにかかわらず、次の各号のいずれかに該当する情報については、機密情報から除外するものとする。
   (1) 開示の時点で既に公知となっていた情報
   (2) 開示の時点で既に受領者が保有していた情報
   (3) 開示後、受領者の責によらず公知となった情報
   (4) 正当な権限を有する第三者から秘密保持義務を負うことなく合法的に入手した情報
3. 本条の規定は、本契約終了後も5年間存続するものとする。

第6条（成果物の帰属）
1. 乙が委託業務の遂行により作成した成果物（以下「成果物」という）の著作権（著作権法第27条および第28条に定める権利を含む）その他一切の知的財産権は、甲に帰属するものとする。
2. 乙は、甲に対し、成果物に関する著作者人格権を行使しないものとする。

第7条（再委託の禁止）
乙は、甲の事前の書面による承諾なく、委託業務の全部または一部を第三者に再委託してはならない。

第8条（契約解除）
1. 甲または乙は、相手方が次の各号のいずれかに該当する場合、何らの催告なく直ちに本契約の全部または一部を解除することができる。
   (1) 本契約に違反し、相当の期間を定めて催告したにもかかわらず、当該期間内に違反が是正されないとき
   (2) 差押、仮差押、仮処分、強制執行または競売の申立てを受けたとき
   (3) 破産手続開始、民事再生手続開始、会社更生手続開始または特別清算開始の申立てがあったとき
   (4) 解散の決議をしたとき
   (5) 手形または小切手が不渡りとなったとき
   (6) その他前各号に準ずる事由が生じたとき
2. 甲または乙は、前項の規定により本契約を解除した場合、相手方に対し、解除によって被った損害の賠償を請求することができる。

第9条（損害賠償）
甲または乙は、本契約に違反して相手方に損害を与えた場合、相手方に対し、その損害を賠償する責任を負う。ただし、天災地変その他不可抗力により生じた損害については、この限りではない。

第10条（反社会的勢力の排除）
1. 甲および乙は、自己またはその役員、従業員が、暴力団、暴力団員、暴力団関係企業・団体またはその関係者、その他反社会的勢力（以下総称して「反社会的勢力」という）でないことを表明し、かつ将来にわたっても該当しないことを確約する。
2. 甲または乙は、相手方が前項に違反した場合、何らの催告なく直ちに本契約の全部または一部を解除することができる。
3. 甲または乙は、相手方が反社会的勢力に該当すると判明した場合、相手方に対し、当該判明時点以降の本契約の履行を拒否することができる。
4. 甲または乙が本条の規定により本契約を解除した場合、解除により相手方に生じた損害の賠償責任を負わない。

第11条（協議解決）
本契約に定めのない事項または本契約の解釈に疑義が生じた場合、甲乙は誠意をもって協議し、解決するものとする。

第12条（管轄裁判所）
本契約に関する一切の紛争については、東京地方裁判所を第一審の専属的合意管轄裁判所とする。

以上、本契約の成立を証するため、本書2通を作成し、甲乙記名押印のうえ、各1通を保有する。

20XX年3月15日

甲：東京都千代田区〇〇町1-2-3
   株式会社ABC
   代表取締役 山田太郎

乙：東京都新宿区△△町4-5-6
   株式会社XYZ
   代表取締役 佐藤花子""")

    # サンプル利用規約
    sample_tos_path = os.path.join(samples_dir, 'sample_tos.txt')
    if not os.path.exists(sample_tos_path):
        with open(sample_tos_path, 'w', encoding='utf-8') as f:
            f.write("""サービス利用規約

第1条（本規約の適用）
1. 本規約は、株式会社サンプル（以下「当社」といいます）が提供するオンラインサービス「サンプルサービス」（以下「本サービス」といいます）の利用に関する条件を定めるものであり、本サービスを利用するすべての者（以下「ユーザー」といいます）に適用されます。
2. ユーザーは、本規約に同意のうえ本サービスを利用するものとし、本サービスを利用した時点で本規約に同意したものとみなします。

第2条（本規約の変更）
1. 当社は、ユーザーの事前の承諾を得ることなく、本規約の内容を変更することができるものとします。
2. 当社は、本規約を変更する場合、変更内容をウェブサイト上に表示するか、またはユーザーに電子メールで通知するものとします。
3. 前項の変更内容の表示または通知後、ユーザーが本サービスを利用した場合、ユーザーは変更後の規約に同意したものとみなします。

第3条（ユーザー登録）
1. 本サービスの利用を希望する者（以下「登録希望者」といいます）は、当社の定める方法により、ユーザー登録の申請を行うものとします。
2. 当社は、登録希望者が以下の各号のいずれかに該当する場合、ユーザー登録を拒否することができるものとします。
   (1) 登録希望者が実在しない場合
   (2) 登録情報に虚偽、誤記または記入漏れがある場合
   (3) 過去に本規約に違反したことがある場合
   (4) その他、当社が不適切と判断した場合
3. ユーザーは、登録情報に変更が生じた場合、速やかに当社の定める方法により変更手続きを行うものとします。

第4条（アカウント管理）
1. ユーザーは、自己の責任においてアカウントおよびパスワードを管理・保管するものとし、これを第三者に利用させ、または貸与、譲渡、名義変更、売買等をしてはならないものとします。
2. アカウントまたはパスワードの管理不十分、使用上の過誤、第三者の使用等によって生じた損害に関する責任はユーザーが負うものとし、当社は一切の責任を負いません。

第5条（利用料金および支払方法）
1. ユーザーは、本サービスを利用する場合、当社が別途定める利用料金を支払うものとします。
2. ユーザーは、利用料金を当社が指定する方法により支払うものとします。支払いに必要な振込手数料その他の費用はユーザーの負担とします。
3. ユーザーが利用料金の支払いを遅滞した場合、年14.6%の割合による遅延損害金を支払うものとします。

第6条（禁止事項）
ユーザーは、本サービスの利用にあたり、以下の各号のいずれかに該当する行為または該当すると当社が判断する行為をしてはならないものとします。
(1) 法令または公序良俗に違反する行為
(2) 犯罪行為に関連する行為
(3) 当社のサーバーまたはネットワークの機能を破壊したり、妨害したりする行為
(4) 当社のサービスの運営を妨害するおそれのある行為
(5) 他のユーザーに関する個人情報等を収集または蓄積する行為
(6) 他のユーザーになりすます行為
(7) 当社のサービスに関連して、反社会的勢力に対して直接または間接に利益を供与する行為
(8) その他、当社が不適切と判断する行為

第7条（本サービスの提供の停止等）
1. 当社は、以下の各号のいずれかに該当する場合、ユーザーに事前に通知することなく、本サービスの全部または一部の提供を停止または中断することができるものとします。
   (1) 本サービスに係るコンピュータシステムの保守点検または更新を行う場合
   (2) 地震、落雷、火災、停電または天災などの不可抗力により、本サービスの提供が困難となった場合
   (3) コンピュータまたは通信回線等が事故により停止した場合
   (4) その他、当社が本サービスの提供が困難と判断した場合
2. 当社は、本サービスの提供の停止または中断により、ユーザーまたは第三者が被ったいかなる不利益または損害について、理由を問わず一切の責任を負わないものとします。

第8条（著作権等）
1. ユーザーは、本サービスを通じて提供されるコンテンツについて、当社または第三者が著作権等の知的財産権を有していることを認識し、これを尊重するものとします。
2. ユーザーは、当社または第三者が権利を有するコンテンツを、複製、公衆送信、頒布、翻案等の方法で利用してはならないものとします。ただし、当社が明示的に許諾した場合を除きます。

第9条（ユーザーコンテンツの取扱い）
1. ユーザーは、本サービスを利用して投稿、アップロードまたは送信したコンテンツ（以下「ユーザーコンテンツ」といいます）について、当社に対し、世界的、非独占的、無償、サブライセンス可能かつ譲渡可能な使用権（複製、公衆送信、頒布、翻案等する権利を含みます）を付与するものとします。
2. ユーザーは、ユーザーコンテンツについて、当社または当社の指定する者に対して著作者人格権を行使しないものとします。
3. 当社は、法令または本規約に違反するユーザーコンテンツを削除することができるものとします。

第10条（免責事項）
1. 当社は、本サービスに関して、その完全性、正確性、確実性、有用性等について、いかなる保証も行わないものとします。
2. 当社は、本サービスに関して、ユーザーと他のユーザーまたは第三者との間において生じた取引、連絡または紛争等について、一切の責任を負いません。
3. 当社は、当社による本サービスの提供の中断、停止、終了、利用不能または変更、ユーザーコンテンツの削除または消失、ユーザーの登録の抹消、本サービスの利用によるデータの消失または機器の故障もしくは損傷、その他本サービスに関連してユーザーが被った損害につき、賠償する責任を一切負わないものとします。

第11条（サービス内容の変更・終了）
1. 当社は、ユーザーに通知することなく、本サービスの内容を変更しまたは本サービスの提供を終了することができるものとします。
2. 当社は、本サービスの提供の終了に伴い、ユーザーに生じた損害について、一切の責任を負いません。

第12条（利用規約違反の場合の措置等）
1. 当社は、ユーザーが本規約に違反した場合、当該ユーザーに事前に通知することなく、本サービスの利用を一時的に停止しまたはユーザーとしての登録を抹消することができるものとします。
2. 前項の場合、当社は、当該ユーザーが既に支払った利用料金を返金する義務を負わないものとします。

第13条（個人情報の取扱い）
当社は、ユーザーの個人情報を、別途定めるプライバシーポリシーに従って取り扱うものとします。

第14条（通知または連絡）
ユーザーと当社との間の通知または連絡は、当社の定める方法によって行うものとします。

第15条（権利義務の譲渡禁止）
ユーザーは、当社の書面による事前の承諾なく、本規約上の地位または本規約に基づく権利もしくは義務を第三者に譲渡してはならないものとします。

第16条（反社会的勢力の排除）
ユーザーは、現在、暴力団、暴力団員、暴力団準構成員、暴力団関係企業、総会屋等、社会運動等標ぼうゴロまたは特殊知能暴力集団等、その他これに準ずる者（以下「反社会的勢力」といいます）に該当しないこと、および次の各号のいずれにも該当しないことを表明し、かつ将来にわたっても該当しないことを確約するものとします。
(1) 反社会的勢力が経営を支配していると認められる関係を有すること
(2) 反社会的勢力が経営に実質的に関与していると認められる関係を有すること
(3) 自己もしくは第三者の不正の利益を図る目的または第三者に損害を加える目的をもってするなど、不当に反社会的勢力を利用していると認められる関係を有すること
(4) 反社会的勢力に対して資金等を提供し、または便宜を供与するなどの関与をしていると認められる関係を有すること
(5) 役員または経営に実質的に関与している者が反社会的勢力と社会的に非難されるべき関係を有すること

第17条（準拠法・管轄裁判所）
1. 本規約の解釈にあたっては、日本法を準拠法とします。
2. 本サービスに関して紛争が生じた場合には、当社の本店所在地を管轄する裁判所を専属的合意管轄とします。

2023年1月1日制定""")

    # サンプルプライバシーポリシー
    sample_policy_path = os.path.join(samples_dir, 'sample_privacy_policy.txt')
    if not os.path.exists(sample_policy_path):
        with open(sample_policy_path, 'w', encoding='utf-8') as f:
            f.write("""プライバシーポリシー

株式会社サンプル（以下「当社」といいます）は、当社が提供するサービス（以下「本サービス」といいます）における個人情報の取扱いについて、以下のとおりプライバシーポリシー（以下「本ポリシー」といいます）を定めます。

1. 個人情報の定義
本ポリシーにおいて、「個人情報」とは、個人情報の保護に関する法律（以下「個人情報保護法」といいます）に定義される「個人情報」を指し、生存する個人に関する情報であって、当該情報に含まれる氏名、生年月日、住所、電話番号、メールアドレス等の記述等により特定の個人を識別できるもの、および他の情報と容易に照合することができ、それにより特定の個人を識別できるものをいいます。

2. 個人情報の収集方法
当社は、以下の方法により個人情報を収集します。
(1) 本サービスの利用登録時に入力された情報
(2) 本サービスの利用に伴い自動的に収集される情報（IPアドレス、クッキー情報、位置情報等）
(3) お問い合わせフォーム等を通じて提供された情報
(4) アンケート等への回答により提供された情報
(5) その他、本サービスの利用に関連して提供された情報

3. 収集する個人情報の項目
当社は、本サービスの提供にあたり、以下の個人情報を収集することがあります。
(1) 氏名
(2) 生年月日
(3) 住所
(4) 電話番号
(5) メールアドレス
(6) クレジットカード情報
(7) IPアドレス、クッキー情報、位置情報等
(8) その他、本サービスの提供に必要な情報

4. 個人情報の利用目的
当社は、収集した個人情報を、以下の目的で利用します。
(1) 本サービスの提供・運営のため
(2) ユーザーからのお問い合わせに対応するため
(3) ユーザーが利用中のサービスの新機能、更新情報、キャンペーン等の案内のため
(4) メンテナンス、重要なお知らせなど必要に応じたご連絡のため
(5) 利用規約に違反したユーザーや、不正・不当な目的でサービスを利用しようとするユーザーの特定をし、ご利用をお断りするため
(6) ユーザーにご自身の登録情報の閲覧や変更、削除、ご利用状況の閲覧を行っていただくため
(7) 有料サービスにおいて、ユーザーに利用料金を請求するため
(8) 上記の利用目的に付随する目的

5. 個人情報の第三者提供
当社は、法令に基づく場合や以下の場合を除き、あらかじめユーザーの同意を得ることなく、個人情報を第三者に提供しません。
(1) 人の生命、身体または財産の保護のために必要がある場合であって、本人の同意を得ることが困難であるとき
(2) 公衆衛生の向上または児童の健全な育成の推進のために特に必要がある場合であって、本人の同意を得ることが困難であるとき
(3) 国の機関もしくは地方公共団体またはその委託を受けた者が法令の定める事務を遂行することに対して協力する必要がある場合であって、本人の同意を得ることにより当該事務の遂行に支障を及ぼすおそれがあるとき
(4) 当社が本サービスの一部を第三者に委託する場合
(5) 当社が合併、会社分割、事業譲渡その他の事由によって個人情報の提供を伴う事業の承継をする場合

6. 個人情報の共同利用
当社は、以下のとおり個人情報の共同利用を行います。
(1) 共同利用する個人情報の項目
   氏名、住所、電話番号、メールアドレス、その他本サービスの提供に必要な情報
(2) 共同利用する者の範囲
   当社グループ会社（子会社および関連会社）
(3) 共同利用する者の利用目的
   上記4に定める利用目的と同様
(4) 共同利用する個人情報の管理について責任を有する者の名称
   株式会社サンプル

7. 個人情報の開示・訂正・削除等
ユーザーは、当社に対して、個人情報保護法に基づき自己の個人情報の開示、訂正、削除、利用停止等を請求することができます。請求をご希望の方は、以下の問い合わせ先までご連絡ください。
なお、請求にあたっては、本人確認のための書類のご提出をお願いする場合があります。

8. Cookie（クッキー）その他の技術の利用
当社のサービスは、Cookie（クッキー）および類似技術を使用することがあります。これらの技術は、当社による本サービスの提供、保護および改善、ユーザーの利便性の向上、効果的な広告の配信のために使用されます。なお、ユーザーは、ブラウザの設定により、Cookieの受け取りを拒否することができますが、その場合、本サービスの一部機能が利用できなくなる可能性があります。

9. セキュリティ対策
当社は、個人情報の漏洩、滅失またはき損を防止するために、アクセス制御、暗号化、ウイルス対策など、合理的な安全対策を講じるものとします。

10. 子どもの個人情報
当社は、13歳未満の子どもから意図的に個人情報を収集することはありません。13歳未満の子どもが個人情報を提供しようとしていることを当社が発見した場合、当該情報の提供を拒否し、提供されている場合は当該情報を速やかに削除するための合理的な措置を講じます。

11. 国外への個人情報の移転
当社は、個人情報を、外国にある第三者（外国のサーバを利用する場合を含む）に提供することがあります。この場合、当社は、個人情報保護法に従い、適切な安全措置を講じます。

12. プライバシーポリシーの変更
当社は、法令の変更、事業内容の変更その他の理由により、本ポリシーを変更することがあります。変更後のプライバシーポリシーは、当社ウェブサイトに掲載された時点で効力を生じるものとします。

13. お問い合わせ先
本ポリシーに関するお問い合わせは、以下の窓口までお願いいたします。

株式会社サンプル
住所：東京都千代田区〇〇町1-2-3
メールアドレス：privacy@example.com

制定日：2023年1月1日
最終改定日：2023年1月1日""")

def main():
    """メイン実行関数"""
    # テンプレートファイルを作成
    create_template_files()
    
    print(f"{Fore.GREEN}法的文書分析ツールを起動します...{Style.RESET_ALL}")
    app.run(debug=True, port=5000)

if __name__ == "__main__":
    main()