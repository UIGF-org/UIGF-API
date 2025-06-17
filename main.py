# main.py
import os
import json
import hashlib
from contextlib import asynccontextmanager
from typing import Dict, Generator, Optional

import redis
import sentry_sdk
import uvicorn
from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sqlalchemy import or_
from sqlalchemy.orm import Session

from api_config import (
    ACCEPTED_LANGUAGES,
    CORE_LANGUAGES,
    API_VERSION,
    DOCS_URL,
    LANGUAGE_PAIRS,
    SENTRY_FULL_URL,
    TOKEN,
    game_name_id_map,
)
from base_logger import logger
from db import crud, models
from db.mysql_db import SessionLocal
from db.schemas import TranslateRequest, TranslateResponse
from fetcher import (
    fetch_genshin_impact_update,
    fetch_starrail_update,
    fetch_zzz_update,
)

# ---------------------------------------------------------------------
# SENTRY
# ---------------------------------------------------------------------
if SENTRY_FULL_URL:

    def _before_send(event, hint):
        exc_info = hint.get("exc_info")
        if exc_info:
            exc_type, exc_value, _ = exc_info
            # Ignore expected client‑side errors (HTTP 4xx)
            if isinstance(exc_value, HTTPException) and exc_value.status_code < 500:
                return None
        return event


    sentry_sdk.init(
        dsn=SENTRY_FULL_URL,
        send_default_pii=True,
        integrations=[
            StarletteIntegration(
                transaction_style="url",
                failed_request_status_codes={403, *range(500, 599)},
            ),
            FastApiIntegration(
                transaction_style="url",
                failed_request_status_codes={403, *range(500, 599)},
            ),
        ],
        before_send=_before_send,
        profiles_sample_rate=1.0,
        ignore_errors=[HTTPException],  # extra belt‑and‑suspenders
    )


# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------
def get_game_id_by_name(name: str) -> Optional[int]:
    return game_name_id_map.get(name)


md5_dict_cache: Dict[str, Dict[str, str]] = {}


# ---------------------------------------------------------------------
# DATABASE SESSION DEPENDENCY
# ---------------------------------------------------------------------
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ---------------------------------------------------------------------
# FASTAPI APP
# ---------------------------------------------------------------------
@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    redis_host = os.getenv("REDIS_HOST", "redis")
    fastapi_app.state.redis_pool = redis.ConnectionPool.from_url(f"redis://{redis_host}", db=0)
    logger.info("Connected to Redis")
    yield


app = FastAPI(
    title="UIGF API",
    summary="Supporting localization API for UIGF‑Org",
    description=(
        "This API provides localization support for various games. "
        "Se[UIGF‑Org](https://github.com/UIGF-org) for details."
    ),
    version=API_VERSION,
    docs_url=DOCS_URL,
    redoc_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------
# ROUTES
# ---------------------------------------------------------------------
@app.get("/", response_class=RedirectResponse, status_code=302)
async def root():
    return "api/v1/docs"


# ---------- translate -------------------------------------------------
@app.post("/translate", response_model=TranslateResponse, tags=["translate"])
async def translate(request_data: TranslateRequest, db: Session = Depends(get_db)):
    lang = request_data.lang.lower()
    if lang not in CORE_LANGUAGES:
        if lang in ACCEPTED_LANGUAGES:
            lang = LANGUAGE_PAIRS[lang]
        else:
            raise HTTPException(status_code=403, detail="Language not supported")

    game_id = get_game_id_by_name(request_data.game)
    if game_id is None:
        raise HTTPException(status_code=403, detail="Game not supported")

    translate_type = request_data.type.lower()

    # -------- text -> id ---------------
    if translate_type == "normal":
        word = request_data.item_name
        if not word:
            raise HTTPException(status_code=400, detail="item_name must be provided")

        column_attr = crud.get_lang_column(lang)
        if not column_attr:
            raise HTTPException(status_code=403, detail="Language not recognized")

        if word.startswith("[") and word.endswith("]"):
            try:
                word_list = json.loads(word)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="item_name must be a valid Python‑style JSON list",
                )
            rows = (
                db.query(column_attr, getattr(column_attr.property.parent.class_, "item_id"))
                .filter_by(game_id=game_id)
                .filter(column_attr.in_(word_list))
                .all()
            )
            text_to_id = {txt: iid for txt, iid in rows if txt}
            return TranslateResponse(item_id=[text_to_id.get(w, 0) for w in word_list])

        row = (
            db.query(getattr(column_attr.property.parent.class_, "item_id"))
            .filter_by(game_id=game_id)
            .filter(column_attr == word)
            .first()
        )
        if not row:
            raise HTTPException(status_code=404, detail="Hash ID not found")
        return TranslateResponse(item_id=row[0], item_name=word)

    # -------- id -> text ---------------
    elif translate_type == "reverse":
        item_id = request_data.item_id
        if not item_id:
            raise HTTPException(status_code=400, detail="item_id must be provided")

        column_attr = crud.get_lang_column(lang)
        if not column_attr:
            raise HTTPException(status_code=403, detail="Language not recognized")

        if item_id.startswith("[") and item_id.endswith("]"):
            item_id_list = json.loads(item_id)
            rows = (
                db.query(getattr(column_attr.property.parent.class_, "item_id"), column_attr)
                .filter_by(game_id=game_id)
                .filter(getattr(column_attr.property.parent.class_, "item_id").in_(item_id_list))
                .all()
            )
            id_to_text = {iid: txt for iid, txt in rows}
            return TranslateResponse(item_name=[id_to_text.get(iid, "") for iid in item_id_list])

        row = (
            db.query(column_attr)
            .filter_by(game_id=game_id, item_id=item_id)
            .first()
        )
        if not row:
            raise HTTPException(status_code=404, detail="Word at this ID not found")
        return TranslateResponse(item_name=row[0], item_id=item_id)

    raise HTTPException(status_code=403, detail="Translate type not supported")


# ---------- identify --------------------------------------------------
@app.get("/identify/{game}/{word}", tags=["translate"])
async def identify_item_in_i18n(game: str, word: str, db: Session = Depends(get_db)):
    game_id = get_game_id_by_name(game)
    if game_id is None:
        raise HTTPException(status_code=404, detail="Game not supported")

    or_clauses = [
        (col := crud.get_lang_column(lang_code)) == word
        for lang_code in CORE_LANGUAGES
        if (col := crud.get_lang_column(lang_code)) is not None
    ]
    if not or_clauses:
        raise HTTPException(status_code=500, detail="No valid language columns found")

    results = (
        db.query(models.I18nDict)
        .filter(models.I18nDict.game_id == game_id, or_(*or_clauses))
        .all()
    )
    if not results:
        raise HTTPException(status_code=404, detail="Hash ID not found")

    reversed_lp = {v: k for k, v in LANGUAGE_PAIRS.items()}
    matched_items = []
    for row in results:
        langs = [
            reversed_lp.get(code, code)
            for code in CORE_LANGUAGES
            if getattr(row, f"{code}_text") == word
        ]
        matched_items.append({"item_id": row.item_id, "matched_langs": langs})

    return {"count": len(matched_items), "matched": matched_items}


# ---------- dict download --------------------------------------------
@app.get("/dict/{game}/{lang}.json", tags=["dictionary"])
async def download_language_dict_json(game: str, lang: str, db: Session = Depends(get_db)):
    lang = lang.lower()
    if lang not in ACCEPTED_LANGUAGES and lang not in {"all", "md5"}:
        if len(lang) == 5 and lang in LANGUAGE_PAIRS:
            lang = LANGUAGE_PAIRS[lang]
        else:
            raise HTTPException(status_code=403, detail="Language not supported")

    file_path = f"dict/{game}/{lang}.json"
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=f"{lang}.json", media_type="application/json")

    if lang in ACCEPTED_LANGUAGES and make_language_dict_json(lang, game, db):
        return FileResponse(path=file_path, filename=f"{lang}.json", media_type="application/json")

    raise HTTPException(status_code=400, detail="Invalid request")


def make_language_dict_json(lang: str, game: str, db: Session) -> bool:
    game_id = get_game_id_by_name(game)
    if not game_id:
        return False
    col_attr = crud.get_lang_column(lang)
    if not col_attr:
        return False

    rows = db.query(models.I18nDict.item_id, col_attr).filter_by(game_id=game_id).all()
    os.makedirs(f"dict/{game}", exist_ok=True)
    lang_dict = {text: iid for iid, text in rows if text}

    with open(f"dict/{game}/{lang}.json", "w", encoding="utf-8") as f:
        json.dump(lang_dict, f, indent=4, ensure_ascii=False)
    return True


# ---------- refresh ---------------------------------------------------
@app.get("/refresh/{game}", tags=["refresh"])
async def refresh(
        game: str,
        background_tasks: BackgroundTasks,
        request: Request,
        x_uigf_token: str = Header(None),
):
    if x_uigf_token != TOKEN:
        raise HTTPException(status_code=403, detail="Token not accepted")

    redis_client = redis.Redis.from_pool(request.app.state.redis_pool)
    logger.info("Received refresh request for %s", game)
    background_tasks.add_task(force_refresh_local_data, game, redis_client)
    return {"status": "Background refresh task added"}


def force_refresh_local_data(game: str, redis_client: redis.Redis):
    db = SessionLocal()
    try:
        if game == "genshin":
            localization_dict, game_id = fetch_genshin_impact_update(), 1
        elif game == "starrail":
            localization_dict, game_id = fetch_starrail_update(), 2
        elif game == "zzz":
            localization_dict, game_id = fetch_zzz_update(), 3
        else:
            logger.error("Unsupported game: %s", game)
            return

        logger.info("Fetched %d items for %s", len(localization_dict), game)
        crud.clear_game_data(db, game_id)
        crud.insert_localization_data(db, redis_client, game_id, localization_dict)
        db.commit()

        for language in CORE_LANGUAGES:
            make_language_dict_json(language, game, db)

        all_dict = {
            language: json.load(open(f"dict/{game}/{language}.json", encoding="utf-8"))
            for language in CORE_LANGUAGES
        }
        with open(f"dict/{game}/all.json", "w", encoding="utf-8") as f:
            json.dump(all_dict, f, indent=4, ensure_ascii=False)

        make_checksum(game)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ---------- checksum --------------------------------------------------
@app.get("/md5/{game}", tags=["checksum"])
async def get_checksum(game: str, background_tasks: BackgroundTasks):
    if game not in game_name_id_map:
        raise HTTPException(status_code=403, detail="Game name not accepted")
    if game not in md5_dict_cache:
        background_tasks.add_task(make_checksum, game)
        return {"status": "No checksum yet; generating"}
    return md5_dict_cache[game]


def make_checksum(game: str):
    if game not in game_name_id_map and game != "all":
        return False

    work_list = [game] if game in game_name_id_map else list(game_name_id_map.keys())
    for g in work_list:
        dict_path = f"dict/{g}"
        os.makedirs(dict_path, exist_ok=True)
        json_files = [f for f in os.listdir(dict_path) if f.endswith(".json") and "md5" not in f]
        if not json_files:
            logger.warning("No JSON dictionary for %s; skipping checksum", g)
            continue

        checksum = {}
        for jf in json_files:
            with open(os.path.join(dict_path, jf), "rb") as rf:
                checksum[jf[:-5]] = hashlib.md5(rf.read()).hexdigest()

        md5_dict_cache[g] = checksum
        with open(os.path.join(dict_path, "md5.json"), "w", encoding="utf-8") as wf:
            json.dump(checksum, wf, indent=2)
    return True


# ---------- debug -----------------------------------------------------
@app.get("/sentry-debug")
async def trigger_error():
    1 / 0  # deliberate ZeroDivisionError to test Sentry


# ---------- startup ---------------------------------------------------
if __name__ == "__main__":
    for gname in game_name_id_map:
        os.makedirs(f"./dict/{gname}", exist_ok=True)
    uvicorn.run(app, host="0.0.0.0", port=8900, proxy_headers=True, forwarded_allow_ips="*")
