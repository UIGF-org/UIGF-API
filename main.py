from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import RedirectResponse, FileResponse
from MysqlConn import MysqlConn
import json
import requests
from api_config import *
import os

for game_name in game_name_id_map.keys():
    if not os.path.exists("./dict/{}".format(game_name)):
        os.makedirs("./dict/{}".format(game_name))
app = FastAPI(docs_url=DOCS_URL, redoc_url=None)
db = MysqlConn(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)


@app.get("/", response_class=RedirectResponse, status_code=302)
async def root():
    return "https://uigf.org"


def get_game_id_by_name(this_game_name: str) -> int | None:
    try:
        return game_name_id_map[this_game_name]
    except KeyError:
        return None


@app.post("/translate/", tags=["translate"])
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
                  % (lang, lang, word.replace("'", "\\'"), game_id)
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
            sql = r"SELECT %s FROM i18n_dict WHERE item_id='%s' AND game_id='%s' LIMIT 1"\
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
    if game_id is None:
        return False

    sql = r"SELECT item_id, %s FROM i18n_dict WHERE game_id='%s'" % (lang + "_text", game_id)
    result = db.fetch_all(sql)
    if result is None:
        raise HTTPException(status_code=404, detail="Hash ID not found")
    else:
        try:
            os.mkdir("dict")
        except FileExistsError:
            pass
        lang_dict = {result[i][1]: result[i][0] for i in range(len(result)) if result[i][1] != ""}
        with open("dict/{}/{}.json".format(this_game_name, lang), "w+", encoding='utf-8') as f:
            json.dump(lang_dict, f, indent=4, separators=(',', ': '), ensure_ascii=False)
    return True


@app.get("/{this_game_name}/dict/{lang}.json", tags=["dictionary"])
async def download_language_dict_json(lang: str, this_game_name: str):
    lang = lang.lower()
    if lang not in ACCEPTED_LANGUAGES and lang != "all":
        raise HTTPException(status_code=403, detail="Language not supported")
    if len(lang) == 5:
        lang = LANGUAGE_PAIRS[lang]

    if os.path.exists("dict/{}/{}.json".format(this_game_name, lang)):
        return FileResponse(path="dict/{}.json".format(lang), filename=LANGUAGE_PAIRS[lang] + ".json",
                            media_type="application/json")
    else:
        make_dict_result = make_language_dict_json(lang, this_game_name)
        if make_dict_result:
            return FileResponse(path="dict/{}.json".format(lang), filename=LANGUAGE_PAIRS[lang] + ".json",
                                media_type="application/json")
        else:
            raise HTTPException(status_code=400, detail="Failed to create dictionary, please try again later")


def force_refresh_local_data(this_game_name: str) -> bool:
    if this_game_name == "genshin":
        target_host = "https://genshin-data.uigf.org/d/latest/"
        avatar_config_file = "ExcelBinOutput/AvatarExcelConfigData.json"
        weapon_config_file = "ExcelBinOutput/WeaponExcelConfigData.json"
        chs_file = "TextMap/TextMapCHS.json"
        cht_file = "TextMap/TextMapCHT.json"
        de_file = "TextMap/TextMapDE.json"
        en_file = "TextMap/TextMapEN.json"
        es_file = "TextMap/TextMapES.json"
        fr_file = "TextMap/TextMapFR.json"
        id_file = "TextMap/TextMapID.json"
        jp_file = "TextMap/TextMapJP.json"
        kr_file = "TextMap/TextMapKR.json"
        pt_file = "TextMap/TextMapPT.json"
        ru_file = "TextMap/TextMapRU.json"
        th_file = "TextMap/TextMapTH.json"
        vi_file = "TextMap/TextMapVI.json"
        game_id = 1
    elif this_game_name == "starrail":
        target_host = "https://raw.githubusercontent.com/Dimbreath/StarRailData/master/"
        avatar_config_file = "ExcelOutput/AvatarConfig.json"
        weapon_config_file = "ExcelOutput/EquipmentConfig.json"
        chs_file = "TextMap/TextMapCN.json"
        cht_file = "TextMap/TextMapCHT.json"
        de_file = "TextMap/TextMapDE.json"
        en_file = "TextMap/TextMapEN.json"
        es_file = "TextMap/TextMapES.json"
        fr_file = "TextMap/TextMapFR.json"
        id_file = "TextMap/TextMapID.json"
        jp_file = "TextMap/TextMapJP.json"
        kr_file = "TextMap/TextMapKR.json"
        pt_file = "TextMap/TextMapPT.json"
        ru_file = "TextMap/TextMapRU.json"
        th_file = "TextMap/TextMapTH.json"
        vi_file = "TextMap/TextMapVI.json"
        game_id = 2
    else:
        print("Failed to refresh data: bad game name")
        return False
    avatar_excel_config_data = json.loads(requests.get(target_host + avatar_config_file).text)
    weapon_excel_config_data = json.loads(requests.get(target_host + weapon_config_file).text)
    chs_dict = json.loads(requests.get(target_host + chs_file).text)
    cht_dict = json.loads(requests.get(target_host + cht_file).text)
    de_dict = json.loads(requests.get(target_host + de_file).text)
    en_dict = json.loads(requests.get(target_host + en_file).text)
    es_dict = json.loads(requests.get(target_host + es_file).text)
    fr_dict = json.loads(requests.get(target_host + fr_file).text)
    id_dict = json.loads(requests.get(target_host + id_file).text)
    jp_dict = json.loads(requests.get(target_host + jp_file).text)
    kr_dict = json.loads(requests.get(target_host + kr_file).text)
    pt_dict = json.loads(requests.get(target_host + pt_file).text)
    ru_dict = json.loads(requests.get(target_host + ru_file).text)
    th_dict = json.loads(requests.get(target_host + th_file).text)
    vi_dict = json.loads(requests.get(target_host + vi_file).text)
    dict_list = [chs_dict, cht_dict, de_dict, en_dict, es_dict, fr_dict, id_dict,
                 jp_dict, kr_dict, pt_dict, ru_dict, th_dict, vi_dict]
    item_list = [avatar_excel_config_data, weapon_excel_config_data]

    # Remove Old Data
    try:
        sql_del1 = r"DELETE FROM `i18n_dict` WHERE game_id='%s'" % game_id
        sql_del2 = r"DELETE FROM `generic_dict` WHERE game_id='%s'" % game_id
        db.execute(sql_del1)
        db.execute(sql_del2)

        for file in os.listdir("dict/" + this_game_name):
            os.remove("dict/" + this_game_name + "/" + file)
    except FileNotFoundError:
        print("dict/{} folder not exist".format(this_game_name))
    except OSError:
        raise HTTPException(status_code=500, detail="Database or IO error")

    # Item list has weapon list and character list
    for this_list in item_list:
        for item in this_list:
            try:
                # Genshin
                this_name_hash_id = str(item["nameTextMapHash"])
                this_item_id = int(item["id"])
            except TypeError:
                # Star Rail
                if len(str(item)) == 4:
                    this_name_hash_id = str(this_list[str(item)]["AvatarName"]["Hash"])
                    this_item_id = int(str(item))
                elif len(str(item)) == 5:
                    this_name_hash_id = str(this_list[str(item)]["EquipmentName"]["Hash"])
                    this_item_id = int(str(item))
                else:
                    print(this_list)
                    raise KeyError("Unknown ID Item")
            name_list = [
                lang_dict[this_name_hash_id].replace("'", "\\'") if this_name_hash_id in lang_dict.keys() else "" for
                lang_dict in dict_list]
            lang_dict = {
                "chs": name_list[0],
                "cht": name_list[1],
                "de": name_list[2],
                "en": name_list[3],
                "es": name_list[4],
                "fr": name_list[5],
                "id": name_list[6],
                "jp": name_list[7],
                "kr": name_list[8],
                "pt": name_list[9],
                "ru": name_list[10],
                "th": name_list[11],
                "vi": name_list[12]
            }
            sql1 = r"INSERT INTO i18n_dict (game_id, item_id, chs_text, cht_text, de_text, en_text, es_text, " \
                   r"fr_text, id_text, jp_text, kr_text, pt_text, ru_text, th_text, vi_text) VALUES (%s, %s, '%s', " \
                   r"'%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
                       game_id, this_item_id, name_list[0], name_list[1],
                       name_list[2], name_list[3], name_list[4], name_list[5], name_list[6],
                       name_list[7], name_list[8], name_list[9], name_list[10],
                       name_list[11], name_list[12])
            db.execute(sql1)

            for k, v in lang_dict.items():
                if v != "":
                    sql2 = r"INSERT INTO generic_dict (game_id, item_id, text, lang) VALUES (%s, %s, '%s', '%s')" % (
                        game_id, this_item_id, v, k)
                    db.execute(sql2)

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
    return True


@app.get("/refresh/{this_game_name}/{token}", tags=["refresh"])
async def refresh(token: str, this_game_name: str, background_tasks: BackgroundTasks):
    if token != TOKEN:
        raise HTTPException(status_code=403, detail="Token not accepted")
    print("Receive request of refresh data for {}".format(this_game_name))
    background_tasks.add_task(force_refresh_local_data, this_game_name=this_game_name)
    return {"status": "Add background task successfully"}
