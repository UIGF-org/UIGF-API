import os
import json
import hashlib
import logging
from typing import Optional, Dict, List, Any
from redis import asyncio as aioredis
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Depends
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, exc
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

import uvicorn

from fetcher import fetch_genshin_impact_update, fetch_zzz_update, fetch_starrail_update
from api_config import game_name_id_map, DOCS_URL
from base_logger import logger
from db.mysql_db import SessionLocal
from db.schemas import TranslateRequest, TranslateResponse


# ------------------------------------------------------------------------
# UTILITY FUNCTIONS
# ------------------------------------------------------------------------
def get_game_id_by_name(this_game_name: str) -> Optional[int]:
    return game_name_id_map.get(this_game_name, None)


# ------------------------------------------------------------------------
# MD5 CACHE
# ------------------------------------------------------------------------
md5_dict_cache: Dict[str, Dict[str, str]] = {}

# ------------------------------------------------------------------------
# FASTAPI APP SETUP
# ------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    try:
        logger.info("Starting FastAPI app")
        redis_host = os.getenv("REDIS_HOST", "redis")
        redis_pool = aioredis.ConnectionPool.from_url(f"redis://{redis_host}", db=0)
        fastapi_app.state.redis = redis_pool
        redis_client = aioredis.Redis.from_pool(redis_pool)
        app.state.mysql = SessionLocal()
        yield
        logger.info("Shutting down FastAPI app")
    finally:
        await fastapi_app.shutdown()


app = FastAPI(docs_url=DOCS_URL, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------------
# ROUTES
# ------------------------------------------------------------------------
@app.get("/", response_class=RedirectResponse, status_code=302)
async def root():
    return "api/v1/docs"


@app.post("/translate", response_model=TranslateResponse, tags=["translate"])
async def translate(request_data: TranslateRequest, request: Request):
    db = request.app.state.mysql
    # Normalize language
    lang = request_data.lang.lower()
    if lang not in ACCEPTED_LANGUAGES:
        # Attempt to convert 5-letter code if possible
        if len(lang) == 5 and lang in LANGUAGE_PAIRS:
            lang = LANGUAGE_PAIRS[lang]
        else:
            raise HTTPException(status_code=403, detail="Language not supported")

    game_id = get_game_id_by_name(request_data.game)
    if game_id is None:
        raise HTTPException(status_code=403, detail="Game not supported")

    translate_type = request_data.type.lower()

    # ------------------------------------------------------------------
    # Translate "normal": from text -> item_id
    # ------------------------------------------------------------------
    if translate_type == "normal":
        word = request_data.item_name
        if not word:
            raise HTTPException(status_code=400, detail="item_name must be provided")

        column_attr = get_lang_column(lang)
        if not column_attr:
            raise HTTPException(status_code=403, detail="Language not recognized")

        if word.startswith("[") and word.endswith("]"):
            # It's a list of words
            word_list = json.loads(word)
            rows = (
                db.query(column_attr, getattr(type(column_attr.property.parent.class_), 'item_id'))
                  .filter_by(game_id=game_id)
                  .filter(column_attr.in_(word_list))
                  .all()
            )
            # build { text_value -> item_id }
            text_to_id_map = {}
            for text_val, item_id_val in rows:
                if text_val:
                    text_to_id_map[text_val] = item_id_val
            # For each in the original list, get item_id
            result_list = [text_to_id_map.get(w, 0) for w in word_list]
            return TranslateResponse(item_id=result_list)
        else:
            # Single word
            row = (
                db.query(getattr(type(column_attr.property.parent.class_), 'item_id'))
                  .filter_by(game_id=game_id)
                  .filter(column_attr == word)
                  .first()
            )
            if not row:
                raise HTTPException(status_code=404, detail="Hash ID not found")
            return TranslateResponse(item_id=row[0])

    # ------------------------------------------------------------------
    # Translate "reverse": from item_id -> text
    # ------------------------------------------------------------------
    elif translate_type == "reverse":
        item_id = request_data.item_id
        if not item_id:
            raise HTTPException(status_code=400, detail="item_id must be provided")

        column_attr = get_lang_column(lang)
        if not column_attr:
            raise HTTPException(status_code=403, detail="Language not recognized")

        if item_id.startswith("[") and item_id.endswith("]"):
            # It's a list
            item_id_list = json.loads(item_id)
            rows = (
                db.query(getattr(type(column_attr.property.parent.class_), 'item_id'), column_attr)
                  .filter_by(game_id=game_id)
                  .filter(getattr(type(column_attr.property.parent.class_), 'item_id').in_(item_id_list))
                  .all()
            )
            id_to_text_map = {r[0]: r[1] for r in rows}
            return_list = [id_to_text_map.get(iid, "") for iid in item_id_list]
            return TranslateResponse(item_name=return_list)
        else:
            # Single
            row = (
                db.query(column_attr)
                  .filter_by(game_id=game_id, item_id=item_id)
                  .first()
            )
            if not row:
                raise HTTPException(status_code=404, detail="Word at this ID not found")
            return TranslateResponse(item_name=row[0])

    else:
        raise HTTPException(status_code=403, detail="Translate type not supported")


@app.get("/identify/{this_game_name}/{word}", tags=["translate"])
async def translate_generic(this_game_name: str, word: str, request: Request):
    """
    Looks for an entry in GenericDict where text == word
    Then returns item_id & a list of languages.
    """
    db = request.app.state.mysql
    game_id = get_game_id_by_name(this_game_name)
    if game_id is None:
        raise HTTPException(status_code=404, detail="Game not supported")

    rows = (
        db.query(GenericDict)
          .filter_by(game_id=game_id, text=word)
          .all()
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Hash ID not found")

    # replicate your logic: collect lang codes => turn them into 5-letter codes if needed
    reversed_lp = {v: k for k, v in LANGUAGE_PAIRS.items()}
    all_langs = []
    for r in rows:
        # e.g. r.lang might be "chs", we want the reversed 5-letter code
        all_langs.append(reversed_lp.get(r.lang, r.lang))

    return {
        "item_id": rows[0].item_id,
        "lang": all_langs
    }


@app.get("/dict/{this_game_name}/{lang}.json", tags=["dictionary"])
async def download_language_dict_json(this_game_name: str, lang: str, request: Request):
    db = request.app.state.mysql
    # Basic sanity checks
    lang = lang.lower()
    if lang not in ACCEPTED_LANGUAGES and lang not in ["all", "md5"]:
        if len(lang) == 5 and lang in LANGUAGE_PAIRS:
            lang = LANGUAGE_PAIRS[lang]
        else:
            raise HTTPException(status_code=403, detail="Language not supported")

    file_path = f"dict/{this_game_name}/{lang}.json"
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            filename=f"{lang}.json",
            media_type="application/json"
        )
    # Else try to create it
    if lang in ACCEPTED_LANGUAGES:
        if make_language_dict_json(lang, this_game_name, db) and os.path.exists(file_path):
            return FileResponse(
                path=file_path,
                filename=f"{lang}.json",
                media_type="application/json"
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to create dictionary.")
    raise HTTPException(status_code=400, detail="Invalid request.")


def make_language_dict_json(lang: str, this_game_name: str, db):
    """ Re-build the dict file for one language. """
    game_id = get_game_id_by_name(this_game_name)
    if not game_id:
        return False
    col_attr = get_lang_column(lang)
    if not col_attr:
        return False

    rows = db.query(I18nDict.item_id, col_attr).filter_by(game_id=game_id).all()

    os.makedirs(f"dict/{this_game_name}", exist_ok=True)
    lang_dict = {}
    for (item_id, text_value) in rows:
        if text_value:
            lang_dict[text_value] = item_id

    with open(f"dict/{this_game_name}/{lang}.json", "w", encoding="utf-8") as f:
        json.dump(lang_dict, f, indent=4, ensure_ascii=False)
    return True


@app.get("/refresh/{this_game_name}/{token}", tags=["refresh"])
async def refresh(this_game_name: str, token: str, background_tasks: BackgroundTasks):
    if token != TOKEN:
        raise HTTPException(status_code=403, detail="Token not accepted")
    logging.info("Received refresh request for %s", this_game_name)
    background_tasks.add_task(force_refresh_local_data, this_game_name)
    return {"status": "Background refresh task added"}


def force_refresh_local_data(this_game_name: str):
    """ Runs as a background task: fetch -> wipe -> insert -> build JSON dict -> MD5. """
    db = next(get_db())  # or create a new session
    try:
        if this_game_name == "genshin":
            localization_dict = fetch_genshin_impact_update()
            game_id = 1
        elif this_game_name == "starrail":
            localization_dict = fetch_starrail_update()
            game_id = 2
        elif this_game_name == "zzz":
            localization_dict = fetch_zzz_update()
            game_id = 3
        else:
            raise HTTPException(status_code=400, detail="Game not supported.")

        logging.info("Fetched %d items from %s", len(localization_dict), this_game_name)

        # Clear old data
        clear_game_data(db, game_id)
        # Insert new data
        insert_localization_data(db, game_id, localization_dict)

        # Build dict files
        for language in ACCEPTED_LANGUAGES:
            make_language_dict_json(language, this_game_name, db)

        # Build all.json
        all_language_dict = {}
        for language in ACCEPTED_LANGUAGES:
            fp = f"dict/{this_game_name}/{language}.json"
            if os.path.exists(fp):
                with open(fp, "r", encoding="utf-8") as f:
                    all_language_dict[language] = json.load(f)
        with open(f"dict/{this_game_name}/all.json", "w", encoding="utf-8") as f:
            json.dump(all_language_dict, f, indent=4, ensure_ascii=False)

        make_checksum(this_game_name)
    finally:
        db.close()


@app.get("/md5/{this_game_name}", tags=["checksum"])
async def get_checksum(this_game_name: str, background_tasks: BackgroundTasks):
    if this_game_name not in game_name_id_map:
        raise HTTPException(status_code=403, detail="Game name not accepted")
    try:
        return md5_dict_cache[this_game_name]
    except KeyError:
        background_tasks.add_task(make_checksum, this_game_name)
        return {"status": "No checksum file at this time. Generating..."}


def make_checksum(this_game_name: str):
    """Generate an MD5 for each .json file. If no .json files, forcibly refresh data."""
    if this_game_name in game_name_id_map:
        work_list = [this_game_name]
    elif this_game_name == "all":
        work_list = list(game_name_id_map.keys())
    else:
        return False

    for g in work_list:
        dict_path = f"dict/{g}"
        if not os.path.exists(dict_path):
            os.makedirs(dict_path)

        file_list = [
            f for f in os.listdir(dict_path)
            if f.endswith(".json") and "md5" not in f
        ]
        # If none exist, force refresh
        if len(file_list) == 0:
            force_refresh_local_data(g)
            file_list = [
                f for f in os.listdir(dict_path)
                if f.endswith(".json") and "md5" not in f
            ]

        checksum_dict = {}
        for json_file in file_list:
            file_full_path = os.path.join(dict_path, json_file)
            with open(file_full_path, "rb") as rf:
                file_bytes = rf.read()
                md5_val = hashlib.md5(file_bytes).hexdigest()
            checksum_dict[json_file.replace(".json", "")] = md5_val

        md5_dict_cache[g] = checksum_dict
        with open(os.path.join(dict_path, "md5.json"), "w", encoding="utf-8") as wf:
            json.dump(checksum_dict, wf, indent=2)

    return True


if __name__ == "__main__":
    # Ensure dict directories exist
    for gname in game_name_id_map.keys():
        os.makedirs(f"./dict/{gname}", exist_ok=True)

    uvicorn.run(app, host="0.0.0.0", port=8900, proxy_headers=True, forwarded_allow_ips="*")