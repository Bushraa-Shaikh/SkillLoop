"""
ADAPTER DESIGN PATTERN
======================
Problem : Google OAuth returns data in its own format.
          The rest of the app expects a standard user dict.
Solution: GoogleAuthAdapter converts Google's response into
          a format our UserModel understands.

Interface (Target)  : AuthProviderInterface
Adaptee             : Google OAuth API
Adapter             : GoogleAuthAdapter
"""

import requests
from urllib.parse import urlencode
from abc import ABC, abstractmethod


# ---------------------------------------------------------------
# TARGET INTERFACE  – what our app expects from any auth provider
# ---------------------------------------------------------------
class AuthProviderInterface(ABC):

    @abstractmethod
    def get_auth_url(self) -> str:
        """Return the URL the user should be redirected to."""
        pass

    @abstractmethod
    def exchange_code(self, code: str) -> dict:
        """Exchange auth code for tokens. Returns token dict."""
        pass

    @abstractmethod
    def get_user_info(self, access_token: str) -> dict:
        """
        Fetch user profile from the provider.
        Must return a normalized dict with keys:
            provider_id, email, name, picture
        """
        pass


# ---------------------------------------------------------------
# ADAPTEE  – raw Google OAuth logic (untouched third-party style)
# ---------------------------------------------------------------
class GoogleOAuthClient:
    """
    Simulates calling Google's OAuth endpoints directly.
    This represents the 'incompatible interface' we are adapting.
    """

    AUTH_URL      = "https://accounts.google.com/o/oauth2/auth"
    TOKEN_URL     = "https://oauth2.googleapis.com/token"
    USERINFO_URL  = "https://www.googleapis.com/oauth2/v3/userinfo"

    def __init__(self, client_id: str, client_secret: str,
                 redirect_uri: str):
        self.client_id     = client_id
        self.client_secret = client_secret
        self.redirect_uri  = redirect_uri

    def build_auth_url(self, scope: str, state: str = "") -> str:
        params = {
            "client_id":     self.client_id,
            "redirect_uri":  self.redirect_uri,
            "response_type": "code",
            "scope":         scope,
            "access_type":   "offline",
            "state":         state,
        }
        return f"{self.AUTH_URL}?{urlencode(params)}"

    def fetch_token(self, code: str) -> dict:
        """POST to Google token endpoint, returns raw token response."""
        payload = {
            "code":          code,
            "client_id":     self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri":  self.redirect_uri,
            "grant_type":    "authorization_code",
        }
        resp = requests.post(self.TOKEN_URL, data=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()   # keys: access_token, id_token, expires_in …

    def fetch_userinfo(self, access_token: str) -> dict:
        """GET Google userinfo endpoint. Returns raw Google profile."""
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = requests.get(self.USERINFO_URL, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
        # Google keys: sub, email, name, picture, email_verified, …


# ---------------------------------------------------------------
# ADAPTER  – bridges GoogleOAuthClient → AuthProviderInterface
# ---------------------------------------------------------------
class GoogleAuthAdapter(AuthProviderInterface):
    """
    Adapter that wraps GoogleOAuthClient and translates its
    Google-specific responses into the normalized format
    the rest of the SkillLoop app expects.
    """

    def __init__(self, client_id: str, client_secret: str,
                 redirect_uri: str):
        # Wrap the adaptee
        self._google = GoogleOAuthClient(client_id, client_secret,
                                         redirect_uri)

    # -- AuthProviderInterface implementation -------------------

    def get_auth_url(self, state: str = "") -> str:
        """Return the Google consent screen URL."""
        return self._google.build_auth_url(
            scope="openid email profile",
            state=state
        )

    def exchange_code(self, code: str) -> dict:
        """
        Exchange the code for tokens.
        Returns normalized token dict:
            { access_token, token_type, expires_in }
        """
        raw = self._google.fetch_token(code)
        # Normalize – hide Google-specific field names
        return {
            "access_token": raw.get("access_token"),
            "token_type":   raw.get("token_type", "Bearer"),
            "expires_in":   raw.get("expires_in", 3600),
        }

    def get_user_info(self, access_token: str) -> dict:
        """
        Fetch profile from Google and normalize to app format.

        Google returns:
            { sub, email, name, picture, email_verified }
        We return:
            { provider_id, email, name, picture, is_verified }
        """
        raw = self._google.fetch_userinfo(access_token)

        # ADAPTATION: rename Google fields → app fields
        return {
            "provider_id": raw.get("sub"),          # Google's user ID
            "email":       raw.get("email"),
            "name":        raw.get("name"),
            "picture":     raw.get("picture"),
            "is_verified": raw.get("email_verified", False),
        }


# ---------------------------------------------------------------
# FACTORY HELPER  – get the right adapter by provider name
# ---------------------------------------------------------------
def get_auth_adapter(provider: str, **kwargs) -> AuthProviderInterface:
    """
    Returns the correct auth adapter for the given provider.
    Makes it easy to add GitHub, LinkedIn etc. later.
    """
    adapters = {
        "google": GoogleAuthAdapter,
    }
    if provider not in adapters:
        raise ValueError(f"Unknown auth provider: {provider}")
    return adapters[provider](**kwargs)