from flask import Flask, request, redirect, session, send_from_directory, jsonify, url_for
import requests
import os
from urllib.parse import quote
from jose import jwt

app = Flask(__name__, static_folder=".")
app.secret_key = os.urandom(24)

# Keycloak設定
KEYCLOAK_URL = "http://keycloak:8080"  # Docker内部通信用
BROWSER_KEYCLOAK_URL = "http://localhost/auth"  # ブラウザリダイレクト用
REALM_NAME = "myrealm"
CLIENT_ID = "myclient"
CLIENT_SECRET = "nTvzesUGTaDEIGfw7drdAyGnwa5KPbNF"  # 実際の環境ではこれは安全に保管する必要があります
REDIRECT_URI = "http://localhost/callback"

@app.route('/')
def home():
    # 静的なindex.htmlを提供
    return send_from_directory('.', 'index.html')

@app.route('/user-info')
def user_info():
    # APIとしてユーザー情報を提供
    user = session.get('user')
    if user:
        return jsonify(user)
    else:
        return jsonify({"error": "Not logged in"}), 401

@app.route('/login')
def login():
    # 認証コードフローの開始
    auth_url = (
        f"{BROWSER_KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/auth"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={quote(REDIRECT_URI)}"
        f"&response_type=code"
        f"&scope=openid profile email"
    )
    return redirect(auth_url)

@app.route('/callback')
def callback():
    # 認証コードを取得
    code = request.args.get('code')

    if not code:
        return 'エラー: 認証コードが見つかりません', 400

    # コードをトークンに交換
    token_url = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/token"
    payload = {
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }

    response = requests.post(token_url, data=payload)

    if response.status_code != 200:
        return f'トークン取得エラー: {response.text}', 400

    # トークンを解析
    tokens = response.json()
    id_token = tokens.get('id_token')

    if not id_token:
        return 'IDトークンが見つかりません', 400

    # トークンからユーザー情報を取得（実際の環境では署名検証が必要）
    user_info = jwt.decode(id_token, '', options={"verify_signature": False, "verify_aud": False, "verify_at_hash": False})

    session['user'] = user_info
    session['access_token'] = tokens.get('access_token')

    return redirect('/')

@app.route('/logout')
def logout():
    # セッションからユーザー情報をクリア
    session.pop('user', None)
    session.pop('access_token', None)

    # Keycloakからログアウト
    logout_url = (
        f"{BROWSER_KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/logout"
        f"?redirect_uri={quote(url_for('home', _external=True))}"
    )

    return redirect(logout_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
