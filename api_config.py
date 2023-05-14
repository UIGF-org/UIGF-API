import os

ACCEPTED_LANGUAGES = ["chs", "cht", "de", "en", "es", "fr", "id", "jp", "kr", "pt", "ru", "th", "vi",
                      "zh-cn", "zh-tw", "de-de", "en-us", "es-es", "fr-fr", "id-id", "ja-jp", "ko-kr", "pt-pt", "ru-ru",
                      "th-th", "vi-vn"]
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
TOKEN = os.environ['TOKEN']
DOCS_URL = os.environ['DOCS_URL']
# MySQL Settings
DB_HOST = os.environ['DB_HOST']
DB_PORT = int(os.environ['DB_PORT'])
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_NAME']

game_name_id_map = {
    "genshin": 1,
    "starrail": 2
}
