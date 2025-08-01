import os
import dotenv
import socket
from base_logger import logger


dotenv.load_dotenv()
ACCEPTED_LANGUAGES = ["chs", "cht", "de", "en", "es", "fr", "id", "jp", "kr", "pt", "ru", "th", "vi",
                      "zh-cn", "zh-tw", "de-de", "en-us", "es-es", "fr-fr", "id-id", "ja-jp", "ko-kr", "pt-pt", "ru-ru",
                      "th-th", "vi-vn"]
CORE_LANGUAGES = ["chs", "cht", "de", "en", "es", "fr", "id", "jp", "kr", "pt", "ru", "th", "vi"]
LANGUAGE_PAIRS = {
    "chs": "zh-cn",
    "cht": "zh-tw",
    "de": "de-de",
    "en": "en-us",
    "es": "es-es",
    "fr": "fr-fr",
    "id": "id-id",
    "jp": "ja-jp",
    "kr": "ko-kr",
    "pt": "pt-pt",
    "ru": "ru-ru",
    "th": "th-th",
    "vi": "vi-vn",
    "zh-cn": "chs",
    "zh-tw": "cht",
    "de-de": "de",
    "en-us": "en",
    "es-es": "es",
    "fr-fr": "fr",
    "id-id": "id",
    "ja-jp": "jp",
    "ko-kr": "kr",
    "pt-pt": "pt",
    "ru-ru": "ru",
    "th-th": "th",
    "vi-vn": "vi",
    "all": "all",
    "md5": "md5"
}
# App Settings
TOKEN = os.getenv("TOKEN", "APITOKEN")
DOCS_URL = os.getenv("DOCS_URL", "/api/v1/docs")
API_VERSION = os.getenv("API_VERSION", "v1")

# MySQL Settings
DB_HOST = os.getenv('DB_HOST', None)
if DB_HOST is None:
    DB_HOST = socket.gethostbyname('host.docker.internal')
logger.info(f"Using Docker gateway: {DB_HOST} as the MySQL host")
DB_PORT = 3306
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_NAME']

game_name_id_map = {
    "genshin": 1,
    "starrail": 2,
    "zzz": 3
}
SENTRY_FULL_URL = os.getenv("SENTRY_FULL_URL", None)
