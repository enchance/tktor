from __future__ import annotations
import os
from abc import ABC



class StrTemplate:
    verification_token: str = 'verification:%s'


# class React:
#     # Frontend paths (no leading /)
#     VERIFY_PATH: str = 'auth/verify-account'
#     REQUEST_VERIFY_PATH: str = 'auth/resend-verification-email'
#     REQUEST_PASSWORD_RESET_PATH: str = 'auth/password-reset'
#     REQUEST_PASSWORD_FORGOT_PATH: str = 'auth/password-forgot'


class Defaults:
    # If you update these roles then update triggers.sql, seeders.sql
    # This is only used for caching
    _roles: list[str] = ('user', 'devtesting')  # data.py


    @property
    def ROLES(self) -> list[str]:  # noqa
        return self._roles


class CommonSettings(ABC):
    APP_CODE = 'BBR'
    APP_NAME = 'Bulma'
    VERSION = '0.1'
    # STATICSITE = SITEURL  # No trailing slash

    # react = React()
    defaults = Defaults()

    # Auth
    VERIFICATION_TOKEN_TTL = 3600 * 3
    SEND_VERIFICATION_EMAIL = True

    # Account
    TIMEZONE = 'UTC'
    DATE_SIMPLE = '%Y-%m-%d'
    LANG = 'en-us'
    THEME = 'dark'
    LIMIT_COUNT = 10
    ACCOUNT_UPDATEABLE_KEYS = {'email', 'username', 'firstname', 'lastname', 'display', 'avatar', 'gender', 'social',
                               'website'}

    # Uploads
    MAX_UPLOAD_SIZE = 1024 * 1024 * 3  # 3MB

    # Caching
    USE_CACHE = True
    ACCOUNT_CACHE_TTL = 3600  # 1hr

    # SMTP
    SMTP_TLS: bool = True
    SEND_EMAILS: bool = True


class ProdSettings(CommonSettings):
    DEBUG = False
    SITENAME = 'Tktor'
    SITETLD = 'tktor.com'
    SITEURL = f'https://{SITETLD}'
    FROM_CHALLENGE_EMAIL = f'challenge@{SITETLD}'


class LocalSettings(CommonSettings):
    DEBUG = True
    SITENAME = 'Tktor'
    SITETLD = 'localhost:8000'
    SITEURL = f'http://{SITETLD}'  # noqa
    FROM_CHALLENGE_EMAIL = f'challenge@{SITETLD}'


class Settings:
    _instance = None


    def __new__(cls):
        if cls._instance is None:
            if os.getenv('ENV', 'development') == 'development':
                cls._instance = LocalSettings()
            else:
                cls._instance = ProdSettings()
        return cls._instance


settings = Settings()
