"""Acquire Coze OAuth access tokens with a service application's RSA key."""

import os
import json
import secrets
import threading
import time
from pathlib import Path

import jwt
import requests


class CozeTokenProvider:
    def __init__(self):
        config_path = Path(os.getenv(
            "COZE_OAUTH_CONFIG_PATH",
            Path(__file__).resolve().parent / "coze_oauth_python_jwt" / "coze_oauth_config.json",
        ))
        config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.is_file() else {}
        self.app_id = (os.getenv("COZE_OAUTH_APP_ID") or config.get("client_id") or "").strip()
        self.key_id = (os.getenv("COZE_OAUTH_KEY_ID") or config.get("public_key_id") or "").strip()
        self.private_key = (os.getenv("COZE_OAUTH_PRIVATE_KEY") or config.get("private_key") or "").replace("\\n", "\n").strip()
        self.api_base = (config.get("coze_api_base") or "https://api.coze.com").rstrip("/")
        self._token = None
        self._expires_at = 0
        self._lock = threading.Lock()

    def get_token(self):
        # Vercel may reuse this process, but a cold start can always request a new token.
        if self._token and time.time() < self._expires_at - 300:
            return self._token
        with self._lock:
            if self._token and time.time() < self._expires_at - 300:
                return self._token
            if not all((self.app_id, self.key_id, self.private_key)):
                raise RuntimeError(
                    "缺少 Coze OAuth 配置文件或 COZE_OAUTH_APP_ID、COZE_OAUTH_KEY_ID、COZE_OAUTH_PRIVATE_KEY"
                )
            if self.api_base != "https://api.coze.com":
                raise RuntimeError("Coze OAuth 应用需与当前 api.coze.com 工作流处于同一站点")

            now = int(time.time())
            assertion = jwt.encode(
                {
                    "iss": self.app_id,
                    "aud": "api.coze.com",
                    "iat": now,
                    "exp": now + 600,
                    "jti": secrets.token_urlsafe(32),
                },
                self.private_key,
                algorithm="RS256",
                headers={"typ": "JWT", "kid": self.key_id},
            )
            response = requests.post(
                f"{self.api_base}/api/permission/oauth2/token",
                headers={"Authorization": f"Bearer {assertion}"},
                json={
                    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                    "duration_seconds": 86399,
                },
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
            token = data.get("access_token")
            # Coze's expires_in field is an absolute Unix timestamp in seconds.
            expires_at = data.get("expires_in")
            if not token or not isinstance(expires_at, (int, float)) or expires_at <= time.time() + 300:
                raise RuntimeError("Coze OAuth 未返回有效的访问令牌和过期时间")
            self._token = token
            self._expires_at = expires_at
            return token

    def invalidate(self):
        with self._lock:
            self._token = None
            self._expires_at = 0
