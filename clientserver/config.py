import os

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    OIDC_CLIENT_SECRETS = os.path.join(BASE_DIR, "client_secrets.json")  # 追加
    OIDC_CLIENT_ID = "my-client"
    OIDC_CLIENT_SECRET = "my-secret"
    OIDC_AUTH_URL = "http://keycloak:8080/realms/myrealm/protocol/openid-connect/auth"
    OIDC_TOKEN_URL = "http://keycloak:8080/realms/myrealm/protocol/openid-connect/token"
    OIDC_USERINFO_URL = "http://keycloak:8080/realms/myrealm/protocol/openid-connect/userinfo"
    OIDC_REDIRECT_URI = "http://localhost:5000/callback"  # ここを統一
