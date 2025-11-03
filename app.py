import os
import re
import json
import zipfile
from collections import defaultdict
from flask import Flask, request, render_template, send_file, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200 MB
app.config['SECRET_KEY'] = 'change_this_secret_for_prod'

# ------------------------------------
# ✅ Token Config
START_TOKENS = 1000
TOKEN_FILE = "static/tokens.json"
# ------------------------------------

DEMO_USER = "vishal"
DEMO_PASS = "1234"

def load_tokens():
    """Load token data from JSON file."""
    if not os.path.exists(TOKEN_FILE):
        return {}
    try:
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_tokens(data):
    """Save token data to JSON file."""
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f, indent=2)

def clean_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', '_', name.strip())

@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    tokens = session.get('tokens', START_TOKENS)
    return render_template('index.html', user=session.get('user', 'vishal'), tokens=tokens)

@app.route('/login', methods=['GET'])
def login():
    if 'user' in session:
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if username == DEMO_USER and password == DEMO_PASS:
        tokens_data = load_tokens()
        # ✅ If user exists, load saved tokens, else create new
        if username not in tokens_data:
            tokens_data[username] = START_TOKENS
            save_tokens(tokens_data)
        session['user'] = username
        session['tokens'] = tokens_data[username]
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/convert', methods=['POST'])
def convert():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    username = session['user']
    tokens_data = load_tokens()
    tokens = tokens_data.get(username, START_TOKENS)

    if tokens <= 0:
        return jsonify({'error': 'No tokens left! Please recharge.'}), 403

    if 'pdf' not in request.files or 'excel' not in request.files:
        return jsonify({'error': 'Both PDF and Excel files are required.'}), 400

    pdf_file = request.files['pdf']
    excel_file = request.files['excel']
    pdf_filename = secure_filename(pdf_file.filename)
    excel_filename = secure_filename(excel_file.filename)

    if not pdf_filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Uploaded file is not a PDF.'}), 400
    if not (excel_filename.lower().endswith('.xlsx') or excel_filename.lower().endswith('.xls')):
        return jsonify({'error': 'Uploaded file is not an Excel (.xlsx/.xls).'}), 400

    output_root = os.path.join(os.getcwd(), "output_temp")
    os.makedirs(output_root, exist_ok=True)

    pdf_path = os.path.join(output_root, pdf_filename)
    excel_path = os.path.join(output_root, excel_filename)
    pdf_file.save(pdf_path)
    excel_file.save(excel_path)

    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        return jsonify({'error': f'Could not read Excel file: {str(e)}'}), 400

    if df.shape[1] < 1:
        return jsonify({'error': 'Excel file must have at least one column with names.'}), 400

    names = df.iloc[:, 0].fillna('').astype(str).tolist()

    try:
        reader = PdfReader(pdf_path)
    except Exception as e:
        return jsonify({'error': f'Could not read PDF file: {str(e)}'}), 400

    num_pages = len(reader.pages)
    if len(names) != num_pages:
        return jsonify({'error': f'Number of names ({len(names)}) does not match number of pages in PDF ({num_pages}).'}), 400

    if tokens < num_pages:
        return jsonify({'error': f'Not enough tokens! You need {num_pages} but have {tokens} left.'}), 403

    output_folder = os.path.join(output_root, 'output_pdfs')
    os.makedirs(output_folder, exist_ok=True)
    name_counts = defaultdict(int)

    for i, name in enumerate(names):
        writer = PdfWriter()
        writer.add_page(reader.pages[i])
        if not name.strip():
            name = f'Page_{i+1:03}'
        clean_name = clean_filename(name)
        name_counts[clean_name] += 1
        if name_counts[clean_name] > 1:
            clean_name = f"{clean_name}_{name_counts[clean_name]}"
        filename = f"{clean_name}.pdf"
        output_path = os.path.join(output_folder, filename)
        with open(output_path, 'wb') as f:
            writer.write(f)

    zip_path = os.path.join(output_root, 'zistal_output.zip')
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(output_folder):
            for fname in files:
                full = os.path.join(root, fname)
                zf.write(full, arcname=fname)

    # ✅ Deduct and save updated tokens
    tokens -= num_pages
    tokens_data[username] = tokens
    save_tokens(tokens_data)
    session['tokens'] = tokens

    return send_file(zip_path, as_attachment=True, download_name='zistal_output.zip')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)



# =======================

@app.route('/convert', methods=['POST'])
def convert():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    username = session['user']
    tokens_data = load_tokens()
    tokens = tokens_data.get(username, START_TOKENS)

    if tokens <= 0:
        return jsonify({
            'error': 'no_tokens',
            'message': 'Please recharge your tokens to continue. Email us at zistal@gmail.com to recharge your balance.'
        }), 403

    if 'pdf' not in request.files or 'excel' not in request.files:
        return jsonify({'error': 'Both PDF and Excel files are required.'}), 400

    pdf_file = request.files['pdf']
    excel_file = request.files['excel']
    pdf_filename = secure_filename(pdf_file.filename)
    excel_filename = secure_filename(excel_file.filename)

    if not pdf_filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Uploaded file is not a PDF.'}), 400
    if not (excel_filename.lower().endswith('.xlsx') or excel_filename.lower().endswith('.xls')):
        return jsonify({'error': 'Uploaded file is not an Excel (.xlsx/.xls).'}), 400

    output_root = os.path.join(os.getcwd(), "output_temp")
    os.makedirs(output_root, exist_ok=True)

    pdf_path = os.path.join(output_root, pdf_filename)
    excel_path = os.path.join(output_root, excel_filename)
    pdf_file.save(pdf_path)
    excel_file.save(excel_path)

    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        return jsonify({'error': f'Could not read Excel file: {str(e)}'}), 400

    if df.shape[1] < 1:
        return jsonify({'error': 'Excel file must have at least one column with names.'}), 400

    names = df.iloc[:, 0].fillna('').astype(str).tolist()

    try:
        reader = PdfReader(pdf_path)
    except Exception as e:
        return jsonify({'error': f'Could not read PDF file: {str(e)}'}), 400

    num_pages = len(reader.pages)
    if len(names) != num_pages:
        return jsonify({'error': f'Number of names ({len(names)}) does not match number of pages in PDF ({num_pages}).'}), 400

    if tokens < num_pages:
        return jsonify({
            'error': 'not_enough_tokens',
            'message': f'You have only {tokens} tokens but need {num_pages}. Please recharge at zistal@gmail.com.'
        }), 403

    output_folder = os.path.join(output_root, 'output_pdfs')
    os.makedirs(output_folder, exist_ok=True)
    name_counts = defaultdict(int)

    for i, name in enumerate(names):
        writer = PdfWriter()
        writer.add_page(reader.pages[i])
        if not name.strip():
            name = f'Page_{i+1:03}'
        clean_name = clean_filename(name)
        name_counts[clean_name] += 1
        if name_counts[clean_name] > 1:
            clean_name = f"{clean_name}_{name_counts[clean_name]}"
        filename = f"{clean_name}.pdf"
        output_path = os.path.join(output_folder, filename)
        with open(output_path, 'wb') as f:
            writer.write(f)

    zip_path = os.path.join(output_root, 'zistal_output.zip')
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(output_folder):
            for fname in files:
                full = os.path.join(root, fname)
                zf.write(full, arcname=fname)

    # ✅ Deduct tokens
    tokens -= num_pages
    tokens_data[username] = tokens
    save_tokens(tokens_data)
    session['tokens'] = tokens

    return send_file(zip_path, as_attachment=True, download_name='zistal_output.zip')
