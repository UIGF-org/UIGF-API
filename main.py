import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import RedirectResponse, FileResponse
from MysqlConn import MysqlConn
import json
import hashlib
from api_config import *
import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fetcher import fetch_genshin_impact_update, fetch_zzz_update, fetch_starrail_update

md5_dict_cache = {}
app = FastAPI(docs_url=DOCS_URL, redoc_url=None)
db = MysqlConn(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=RedirectResponse, status_code=302)
async def root():
    return "api/v1/docs"


def get_game_id_by_name(this_game_name: str) -> int | None:
    return game_name_id_map.get(this_game_name, None)

@app.post("/translate", tags=["translate"])
async def translate(request: Request):
    # Handle Parameters
    request = await request.json()
    translate_type = request.get("type")
    lang = request.get("lang").lower()
    if lang not in ACCEPTED_LANGUAGES:
        raise HTTPException(status_code=403, detail="Language not supported")
    if len(lang) == 5:
        lang = LANGUAGE_PAIRS[lang]
    game_id = get_game_id_by_name(request.get("game"))
    if game_id is None:
        raise HTTPException(status_code=403, detail="Game not supported")

    if translate_type == "normal":
        word = request.get("item_name")
        if word.startswith("[") and word.endswith("]"):
            # Make list with original order
            word_list = json.loads(word.replace(',', '","').replace('[', '["').replace(']', '"]'))
            # Generate temp dict for look up
            word = word.strip('][')
            word = '"' + word.replace(',', '","') + '"'
            sql = r"SELECT %s, item_id FROM i18n_dict WHERE %s IN (%s) AND game_id='%s'" \
                  % (lang + "_text", lang + "_text", word.replace("'", "\\'"), game_id)
            # This SQL result will return all text and their ID in a dict, no duplicate keys
            result = db.fetch_all(sql)
            if result is None:
                raise HTTPException(status_code=404, detail="Hash ID not found")
            else:
                # Translate the list with the dict
                result_dict = {result[i][0]: result[i][1] for i in range(len(result)) if result[i][0] != ""}
                # Return 0 if not found
                result_list = [result_dict[word] if word in result_dict.keys() else 0 for word in word_list]
                return {"item_id": result_list}
        else:
            sql = r"SELECT item_id FROM i18n_dict WHERE %s='%s' AND game_id='%s' LIMIT 1" \
                  % (lang + "_text", word.replace("'", "\\'"), game_id)
            result = db.fetch_one(sql)
            if result is None:
                raise HTTPException(status_code=404, detail="Hash ID not found")
            else:
                return {"item_id": result[0]}
    elif translate_type == "reverse":
        item_id = request.get("item_id")
        if item_id.startswith("[") and item_id.endswith("]"):
            item_id_list = json.loads(item_id)
            item_id = item_id.replace("[", "").replace("]", "")
            sql = r"SELECT item_id, %s FROM i18n_dict WHERE item_id IN (%s) AND game_id='%s'" \
                  % (lang + "_text", item_id.replace("'", "\\'"), game_id)
            result = db.fetch_all(sql)
            this_request_dict = {item[0]: item[1] for item in result}
            return_list = [this_request_dict[item_id] if item_id in this_request_dict.keys()
                           else "" for item_id in item_id_list]
            return {"item_name": return_list}
        else:
            sql = r"SELECT %s FROM i18n_dict WHERE item_id='%s' AND game_id='%s' LIMIT 1" \
                  % (lang + "_text", item_id, game_id)
            result = db.fetch_one(sql)
            if result is None:
                raise HTTPException(status_code=404, detail="Word at this ID not found")
            else:
                return {"item_name": result[0]}
    else:
        raise HTTPException(status_code=403, detail="Translate type not supported")


@app.get("/identify/{this_game_name}/{word}", tags=["translate"])
async def translate_generic(word: str, this_game_name: str):
    game_id = get_game_id_by_name(this_game_name)
    if game_id is None:
        return False

    sql = r"SELECT item_id, lang FROM generic_dict WHERE text='%s' AND game_id='%s'" % (word.replace("'", "\\'"),
                                                                                        game_id)
    result = db.fetch_all(sql)
    if len(result) == 0:
        raise HTTPException(status_code=404, detail="Hash ID not found")
    else:
        return {"item_id": result[0][0],
                "lang": [LANGUAGE_PAIRS[result[i][1]] for i in range(len(result))]}


def make_language_dict_json(lang: str, this_game_name: str) -> bool:
    lang = lang.lower()
    if lang not in ACCEPTED_LANGUAGES:
        return False
    if len(lang) == 5:
        lang = LANGUAGE_PAIRS[lang]

    game_id = get_game_id_by_name(this_game_name)
    if not game_id:
        return False

    sql = r"SELECT item_id, %s FROM i18n_dict WHERE game_id='%s'" % (lang + "_text", game_id)
    result = db.fetch_all(sql)
    if result is None:
        raise HTTPException(status_code=404, detail="Hash ID not found")
    else:
        os.makedirs("dict", exist_ok=True)
        lang_dict = {result[i][1]: result[i][0] for i in range(len(result)) if result[i][1] != ""}
        with open("dict/{}/{}.json".format(this_game_name, lang), "w+", encoding='utf-8') as f:
            json.dump(lang_dict, f, indent=4, separators=(',', ': '), ensure_ascii=False)
    return True


@app.get("/dict/{this_game_name}/{lang}.json", tags=["dictionary"])
async def download_language_dict_json(lang: str, this_game_name: str):
    lang = lang.lower()
    if lang not in ACCEPTED_LANGUAGES and lang != "all" and lang != "md5":
        raise HTTPException(status_code=403, detail="Language not supported")
    if len(lang) == 5:
        lang = LANGUAGE_PAIRS[lang]

    if os.path.exists("dict/{}/{}.json".format(this_game_name, lang)):
        return FileResponse(path="dict/{}/{}.json".format(this_game_name, lang),
                            filename=LANGUAGE_PAIRS[lang] + ".json", media_type="application/json")
    else:
        make_dict_result = make_language_dict_json(lang, this_game_name)
        if make_dict_result:
            return FileResponse(path="dict/{}.json".format(lang), filename=LANGUAGE_PAIRS[lang] + ".json",
                                media_type="application/json")
        else:
            raise HTTPException(status_code=400, detail="Failed to create dictionary, please try again later")


def force_refresh_local_data(this_game_name: str) -> bool:
    print("Start refreshing data for {}".format(this_game_name))
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
        raise HTTPException(status_code=400, detail="Game not supported")
    print(f"Successfully fetched {len(localization_dict)} items from {this_game_name}")


    # Remove Old Data
    try:
        sql_del1 = r"DELETE FROM `i18n_dict` WHERE game_id='%s'" % game_id
        sql_del2 = r"DELETE FROM `generic_dict` WHERE game_id='%s'" % game_id
        db.execute(sql_del1)
        db.execute(sql_del2)
    except OSError:
        raise HTTPException(status_code=500, detail="Database or IO error")
    print("Successfully removed old data")

    # Item list has weapon list and character list
    for item_id,translation in localization_dict.items():
        print(f"Processing item {item_id}")
        sql1 = r"INSERT INTO i18n_dict (game_id, item_id, chs_text, cht_text, de_text, en_text, es_text, " \
               r"fr_text, id_text, jp_text, kr_text, pt_text, ru_text, th_text, vi_text) VALUES (%s, %s, '%s', " \
               r"'%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
                   game_id, item_id, translation["chs"], translation["cht"],
                   translation["de"], translation["en"], translation["es"], translation["fr"], translation["id"],
                   translation["jp"], translation["kr"], translation["pt"], translation["ru"],
                   translation["th"], translation["vi"])
        db.execute(sql1)

        for lang, text in translation.items():
            if text != "":
                sql2 = r"INSERT INTO generic_dict (game_id, item_id, text, lang) VALUES (%s, %s, '%s', '%s')" % (
                    game_id, item_id, lang, text)
                db.execute(sql2)
        print(f"Successfully inserted item {item_id} into database")

    print("Successfully made data in database; continue make file")

    # Make dict files for each language
    for language in ACCEPTED_LANGUAGES:
        if len(language) != 5:
            if not make_language_dict_json(language, this_game_name):
                print("Failed to made dict file for %s for %s" % (language, this_game_name))
                return False
        print("Successfully made dict file for %s for %s" % (language, this_game_name))

    # Make a dict for all languages
    all_language_dict = {}
    for language in ACCEPTED_LANGUAGES:
        if len(language) != 5:
            this_lang_dict = json.loads(open("./dict/{}/{}.json".format(this_game_name, language),
                                             "r", encoding="utf-8").read())
            all_language_dict[language] = this_lang_dict
            print("Loaded " + language + " dict for " + this_game_name)
    open("dict/%s/all.json" % this_game_name, "w", encoding="utf-8").write(
        json.dumps(all_language_dict, ensure_ascii=False, indent=4))
    print("Successfully generated dict/%s/all.json" % this_game_name)
    make_checksum(this_game_name)
    return True


@app.get("/refresh/{this_game_name}/{token}", tags=["refresh"])
async def refresh(token: str, this_game_name: str, background_tasks: BackgroundTasks):
    if token != TOKEN:
        raise HTTPException(status_code=403, detail="Token not accepted")
    print("Receive request of refresh data for {}".format(this_game_name))
    background_tasks.add_task(force_refresh_local_data, this_game_name=this_game_name)
    return {"status": "Add background task successfully"}


def make_checksum(this_game_name: str):
    if this_game_name in game_name_id_map.keys():
        work_list = [this_game_name]
    elif this_game_name == "all":
        work_list = game_name_id_map.keys()
    else:
        return False

    for g in work_list:
        if len(os.listdir("./dict/{}".format(g))) == 0:
            print("Find empty dict folder during checksum. Force make data.")
            force_refresh_local_data(g)

        file_list = [f for f in os.listdir("./dict/{}".format(g)) if f.endswith(".json") and "md5" not in f]
        print(file_list)
        checksum_dict = {}
        for json_file in file_list:
            with open("./dict/{}/{}".format(g, json_file), "rb") as f:
                b = f.read()
                md5_hash = hashlib.md5(b).hexdigest()
            checksum_dict[json_file.replace(".json", "")] = md5_hash
            print("Successfully generate MD5 of {} language file for {}".format(json_file, g))
        md5_dict_cache[g] = checksum_dict
        with open("./dict/{}/md5.json".format(g), "w+") as write_file:
            json.dump(checksum_dict, write_file, indent=2)
        print("Finished the checksum task for {}".format(g))
    print("MD5 file generated")
    return True


@app.get("/md5/{this_game_name}", tags=["checksum"])
async def get_checksum(this_game_name: str, background_tasks: BackgroundTasks):
    if this_game_name not in game_name_id_map.keys():
        raise HTTPException(status_code=403, detail="Game name not accepted")
    try:
        return md5_dict_cache[this_game_name]
    except KeyError:
        background_tasks.add_task(make_checksum, this_game_name=this_game_name)
        return {"status": "No checksum file at this time, come back later."}


if __name__ == "__main__":
    for game_name in game_name_id_map.keys():
        if not os.path.exists("./dict/{}".format(game_name)):
            os.makedirs("./dict/{}".format(game_name))
    uvicorn.run(app, host="0.0.0.0", port=8900, proxy_headers=True, forwarded_allow_ips="*")
