from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import RedirectResponse, FileResponse
from MysqlConn import MysqlConn
import json
import requests
from api_config import *

app = FastAPI(docs_url=DOCS_URL, redoc_url=None)
db = MysqlConn(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)


@app.get("/", response_class=RedirectResponse, status_code=302)
async def root():
    return "https://uigf.org"


@app.post("/translate/", tags=["translate"])
async def translate(request: Request):
    # Handle Parameters
    request = await request.json()
    translate_type = request.get("type")
    lang = request.get("lang")
    lang = lang.lower()
    if lang not in ACCEPTED_LANGUAGES:
        raise HTTPException(status_code=403, detail="Language not supported")
    if len(lang) == 5:
        lang = LANGUAGE_PAIRS[lang]

    if translate_type == "normal":
        word = request.get("item_name")
        if word.startswith("[") and word.endswith("]"):
            # Make list with original order
            word_list = json.loads(word.replace(',', '","').replace('[', '["').replace(']', '"]'))
            # Generate temp dict for look up
            word = word.strip('][')
            word = '"' + word.replace(',', '","') + '"'
            sql = r"SELECT %s, item_id FROM i18n_dict WHERE %s IN (%s)" % (lang, lang, word.replace("'", "\\'"))
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
            sql = r"SELECT item_id FROM i18n_dict WHERE %s='%s' LIMIT 1" % (lang, word.replace("'", "\\'"))
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
            sql = r"SELECT item_id, %s FROM i18n_dict WHERE item_id IN (%s)" % (lang, item_id.replace("'", "\\'"))
            result = db.fetch_all(sql)
            this_request_dict = {item[0]: item[1] for item in result}
            return_list = [this_request_dict[item_id] if item_id in this_request_dict.keys()
                           else "" for item_id in item_id_list]
            return {"item_name": return_list}
        else:
            sql = r"SELECT %s FROM i18n_dict WHERE item_id='%s' LIMIT 1" % (lang, item_id)
            print(sql)
            result = db.fetch_one(sql)
            if result is None:
                raise HTTPException(status_code=404, detail="Word at this ID not found")
            else:
                return {"item_name": result[0]}
    else:
        raise HTTPException(status_code=403, detail="Translate type not supported")


@app.get("/generic-translate/{word}", tags=["translate"])
async def translate_generic(word: str):
    sql = r"SELECT item_id, lang FROM generic_dict WHERE text='%s'" % word.replace("'", "\\'")
    result = db.fetch_all(sql)
    if len(result) == 0:
        raise HTTPException(status_code=404, detail="Hash ID not found")
    else:
        return {"item_id": result[0][0],
                "lang": [LANGUAGE_PAIRS[result[i][1]] for i in range(len(result))]}


def make_language_dict_json(lang: str):
    lang = lang.lower()
    if lang not in ACCEPTED_LANGUAGES:
        return False
    if len(lang) == 5:
        lang = LANGUAGE_PAIRS[lang]
    sql = r"SELECT item_id, %s FROM i18n_dict" % lang.lower()
    result = db.fetch_all(sql)
    if result is None:
        raise HTTPException(status_code=404, detail="Hash ID not found")
    else:
        try:
            os.mkdir("dict")
        except FileExistsError:
            pass
        lang_dict = {result[i][1]: result[i][0] for i in range(len(result)) if result[i][1] != ""}
        with open("dict/" + lang + ".json", 'w+', encoding='utf-8') as f:
            json.dump(lang_dict, f, indent=4, separators=(',', ': '), ensure_ascii=False)


@app.get("/dict/{lang}.json", tags=["dictionary"])
async def download_language_dict_json(lang: str):
    lang = lang.lower()
    if lang not in ACCEPTED_LANGUAGES and lang != "all":
        raise HTTPException(status_code=403, detail="Language not supported")
    if len(lang) == 5:
        lang = LANGUAGE_PAIRS[lang]

    if os.path.exists("dict/" + lang + ".json"):
        return FileResponse(path="dict/" + lang + ".json", filename=LANGUAGE_PAIRS[lang] + ".json",
                            media_type="application/json")
    else:
        make_dict_result = make_language_dict_json(lang)
        if make_dict_result:
            return FileResponse(path="dict/" + lang + ".json", filename=LANGUAGE_PAIRS[lang] + ".json",
                                media_type="application/json")
        else:
            raise HTTPException(status_code=400, detail="Failed to create dictionary, please try again later")


def force_refresh_local_data():
    AvatarExcelConfigData = json.loads(requests.get("https://genshin-data.uigf.org/d/latest/"
                                                    "ExcelBinOutput/AvatarExcelConfigData.json").text)
    WeaponExcelConfigData = json.loads(requests.get("https://genshin-data.uigf.org/d/latest/"
                                                    "/ExcelBinOutput/WeaponExcelConfigData.json").text)
    chs_dict = json.loads(
        requests.get("https://genshin-data.uigf.org/d/latest/TextMap/TextMapCHS.json").text)
    cht_dict = json.loads(
        requests.get("https://genshin-data.uigf.org/d/latest/TextMap/TextMapCHT.json").text)
    de_dict = json.loads(
        requests.get("https://genshin-data.uigf.org/d/latest/TextMap/TextMapDE.json").text)
    en_dict = json.loads(
        requests.get("https://genshin-data.uigf.org/d/latest/TextMap/TextMapEN.json").text)
    es_dict = json.loads(
        requests.get("https://genshin-data.uigf.org/d/latest/TextMap/TextMapES.json").text)
    fr_dict = json.loads(
        requests.get("https://genshin-data.uigf.org/d/latest/TextMap/TextMapFR.json").text)
    id_dict = json.loads(
        requests.get("https://genshin-data.uigf.org/d/latest/TextMap/TextMapID.json").text)
    jp_dict = json.loads(
        requests.get("https://genshin-data.uigf.org/d/latest/TextMap/TextMapJP.json").text)
    kr_dict = json.loads(
        requests.get("https://genshin-data.uigf.org/d/latest/TextMap/TextMapKR.json").text)
    pt_dict = json.loads(
        requests.get("https://genshin-data.uigf.org/d/latest/TextMap/TextMapPT.json").text)
    ru_dict = json.loads(
        requests.get("https://genshin-data.uigf.org/d/latest/TextMap/TextMapRU.json").text)
    th_dict = json.loads(
        requests.get("https://genshin-data.uigf.org/d/latest/TextMap/TextMapTH.json").text)
    vi_dict = json.loads(
        requests.get("https://genshin-data.uigf.org/d/latest/TextMap/TextMapVI.json").text)
    dict_list = [chs_dict, cht_dict, de_dict, en_dict, es_dict, fr_dict, id_dict,
                 jp_dict, kr_dict, pt_dict, ru_dict, th_dict, vi_dict]

    item_list = [AvatarExcelConfigData, WeaponExcelConfigData]

    try:
        sql_del1 = r"TRUNCATE `uigf_dict`.`i18n_dict`"
        sql_del2 = r"TRUNCATE `uigf_dict`.`generic_dict`"
        db.execute(sql_del1)
        db.execute(sql_del2)

        for file in os.listdir("dict"):
            os.remove("dict/" + file)
    except:
        raise HTTPException(status_code=500, detail="Database or IO error")

    # Item list has weapon list and character list
    for this_list in item_list:
        for item in this_list:
            this_name_hash_id = str(int(item["nameTextMapHash"]))
            this_item_id = int(item["id"])
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

            sql1 = r"INSERT INTO i18n_dict (item_id, chs, cht, de, en, es, fr, id, jp, kr, pt, ru, th, vi) VALUES" \
                   r" (%s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
                       this_item_id, name_list[0], name_list[1],
                       name_list[2], name_list[3], name_list[4], name_list[5], name_list[6],
                       name_list[7], name_list[8], name_list[9], name_list[10],
                       name_list[11], name_list[12])
            db.execute(sql1)

            for key_name in lang_dict.keys():
                if lang_dict[key_name] != "":
                    sql2 = r"INSERT INTO generic_dict (item_id, text, lang) VALUES (%s, '%s', '%s')" % (
                        this_item_id, lang_dict[key_name], key_name)
                    db.execute(sql2)

    # Make dict files for each language
    for language in ACCEPTED_LANGUAGES:
        if len(language) != 5:
            make_language_dict_json(language)
        print("Successfully made dict file for %s" % language)

    # Make a dict for all languages
    all_language_dict = {}
    for language in ACCEPTED_LANGUAGES:
        if len(language) != 5:
            this_lang_dict = json.loads(open("dict/" + language + ".json", "r", encoding="utf-8").read())
            all_language_dict[language] = this_lang_dict
            print("Loaded " + language + " dict")
    open("dict/all.json", "w", encoding="utf-8").write(json.dumps(all_language_dict, ensure_ascii=False, indent=4))
    print("Successfully generated dict/all.json")


@app.get("/refresh/{token}", tags=["refresh"])
async def refresh(token: str, background_tasks: BackgroundTasks):
    if token != TOKEN:
        raise HTTPException(status_code=403, detail="Token not accepted")
    background_tasks.add_task(force_refresh_local_data)
    return {"status": "Add background task successfully"}
