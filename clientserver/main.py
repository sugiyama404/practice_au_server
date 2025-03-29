from flask import Flask, redirect, url_for, session, jsonify, request
from flask_oidc import OpenIDConnect
from config import Config
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config.update({
    "OIDC_CLIENT_SECRETS": Config.OIDC_CLIENT_SECRETS,  # ここを修正
    "OIDC_CLIENT_ID": Config.OIDC_CLIENT_ID,
    "OIDC_CLIENT_SECRET": Config.OIDC_CLIENT_SECRET,
    "OIDC_CALLBACK_ROUTE": "/callback",
    "OIDC_SCOPES": ["openid", "profile", "email"],
    "OIDC_ISSUER": Config.OIDC_AUTH_URL,
    "OIDC_USERINFO_ENDPOINT": Config.OIDC_USERINFO_URL,
    "OIDC_TOKEN_ENDPOINT": Config.OIDC_TOKEN_URL,
    "SECRET_KEY": "random_secret_key",
    "DEBUG": True,
})

oidc = OpenIDConnect(app)

@app.route("/")
def home():
    if oidc.user_loggedin:
        return f"Hello, {oidc.user_getfield('email')}!"
    else:
        return 'Welcome! <a href="/login">Login</a>'

@app.route("/login")
def login():
    # ランダムな state を生成してセッションに保存
    state = os.urandom(24).hex()
    session['state'] = state

    # 認証リクエストを作成し、state を含めてリダイレクト
    auth_url = oidc.client_secrets['auth_uri'] + "?response_type=code&client_id=my-client&redirect_uri=http://localhost:8000/callback&state=" + state
    return redirect(auth_url)

@app.route("/logout")
def logout():
    oidc.logout()
    return redirect(url_for("home"))

@app.route("/user")
def user_info():
    if oidc.user_loggedin:
        return jsonify(oidc.user_getinfo(["sub", "name", "email"]))
    return "Not logged in", 401

@app.route('/callback')
def callback():
    # 認証後に受け取った state とセッションの state を比較
    if request.args.get('state') != session.get('state'):
        return "CSRF Warning! State not equal in request and response", 400

    # 認証が成功した場合、ユーザー情報を取得して処理
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
