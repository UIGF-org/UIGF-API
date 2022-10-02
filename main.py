from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse, FileResponse
from MysqlConn import MysqlConn
import json
import os
import requests
from config.api_config import ACCEPTED_LANGUAGES, TOKEN, DOCS_URL

app = FastAPI(docs_url=DOCS_URL, redoc_url=None)
db = MysqlConn()


@app.get("/", response_class=RedirectResponse, status_code=302)
async def root():
    return "https://uigf.org"


@app.get("/translate/{lang}/{word}", tags=["translate"])
async def translate(lang: str, word: str):
    lang = lang.lower()
    if lang not in ACCEPTED_LANGUAGES:
        raise HTTPException(status_code=403, detail="Language not supported")

    if word.startswith("[") and word.endswith("]"):
        # Make list with original order
        word_list = json.loads(word.replace(',', '","').replace('[', '["').replace(']', '"]'))
        print(word_list)
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
        sql = r"SELECT item_id FROM i18n_dict WHERE %s='%s'" % (lang, word.replace("'", "\\'"))
        result = db.fetch_one(sql)
        if result is None:
            raise HTTPException(status_code=404, detail="Hash ID not found")
        else:
            return {"item_id": result[0]}


@app.get("/generic-translate/{word}", tags=["translate"])
async def translate_generic(word: str):
    sql = r"SELECT item_id, lang FROM generic_dict WHERE text='%s'" % word.replace("'", "\\'")
    result = db.fetch_all(sql)
    if result is None:
        raise HTTPException(status_code=404, detail="Hash ID not found")
    else:
        return {"item_id": result[0][0],
                "lang": [result[i][1] for i in range(len(result))]}


def make_language_dict_json(lang: str):
    lang = lang.lower()
    if lang not in ACCEPTED_LANGUAGES:
        return False
    sql = r"SELECT item_id, %s FROM i18n_dict" % lang.lower()
    result = db.fetch_all(sql)
    if result is None:
        raise HTTPException(status_code=404, detail="Hash ID not found")
    else:
        try:
            os.mkdir("dict")
        except FileExistsError:
            print("dict folder already exists")
        lang_dict = {result[i][1]: result[i][0] for i in range(len(result)) if result[i][1] != ""}
        with open("dict/" + lang + ".json", 'w+', encoding='utf-8') as f:
            json.dump(lang_dict, f, indent=4, separators=(',', ': '), ensure_ascii=False)


@app.get("/dict/{lang}.json", tags=["dictionary"])
async def download_language_dict_json(lang: str):
    lang = lang.lower()
    if lang not in ACCEPTED_LANGUAGES:
        raise HTTPException(status_code=403, detail="Language not supported")

    if os.path.exists("dict/" + lang + ".json"):
        return FileResponse(path="dict/" + lang + ".json", filename=lang + ".json", media_type="application/json")
    else:
        make_dict_result = make_language_dict_json(lang)
        if make_dict_result:
            return FileResponse(path="dict/" + lang + ".json", filename=lang + ".json", media_type="application/json")
        else:
            raise HTTPException(status_code=400, detail="Failed to create dictionary, please try again later")


def force_refresh_local_data():
    AvatarExcelConfigData = json.loads(requests.get("https://github.com/Dimbreath/GenshinData/raw/master" \
                                                    "/ExcelBinOutput/AvatarExcelConfigData.json").text)
    WeaponExcelConfigData = json.loads(requests.get("https://github.com/Dimbreath/GenshinData/raw/master" \
                                                    "/ExcelBinOutput/WeaponExcelConfigData.json").text)
    chs_dict = json.loads(
        requests.get("https://github.com/Dimbreath/GenshinData/raw/master/TextMap/TextMapCHS.json").text)
    cht_dict = json.loads(
        requests.get("https://github.com/Dimbreath/GenshinData/raw/master/TextMap/TextMapCHT.json").text)
    de_dict = json.loads(
        requests.get("https://github.com/Dimbreath/GenshinData/raw/master/TextMap/TextMapDE.json").text)
    en_dict = json.loads(
        requests.get("https://github.com/Dimbreath/GenshinData/raw/master/TextMap/TextMapEN.json").text)
    es_dict = json.loads(
        requests.get("https://github.com/Dimbreath/GenshinData/raw/master/TextMap/TextMapES.json").text)
    fr_dict = json.loads(
        requests.get("https://github.com/Dimbreath/GenshinData/raw/master/TextMap/TextMapFR.json").text)
    id_dict = json.loads(
        requests.get("https://github.com/Dimbreath/GenshinData/raw/master/TextMap/TextMapID.json").text)
    jp_dict = json.loads(
        requests.get("https://github.com/Dimbreath/GenshinData/raw/master/TextMap/TextMapJP.json").text)
    kr_dict = json.loads(
        requests.get("https://github.com/Dimbreath/GenshinData/raw/master/TextMap/TextMapKR.json").text)
    pt_dict = json.loads(
        requests.get("https://github.com/Dimbreath/GenshinData/raw/master/TextMap/TextMapPT.json").text)
    ru_dict = json.loads(
        requests.get("https://github.com/Dimbreath/GenshinData/raw/master/TextMap/TextMapRU.json").text)
    th_dict = json.loads(
        requests.get("https://github.com/Dimbreath/GenshinData/raw/master/TextMap/TextMapTH.json").text)
    vi_dict = json.loads(
        requests.get("https://github.com/Dimbreath/GenshinData/raw/master/TextMap/TextMapVI.json").text)

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
            this_name_hash_id = int(item["nameTextMapHash"])
            this_item_id = int(item["id"])
            try:
                chs_name = chs_dict[str(this_name_hash_id)].replace("'", "\\'")
            except KeyError:
                chs_name = ""
            try:
                cht_name = cht_dict[str(this_name_hash_id)].replace("'", "\\'")
            except KeyError:
                cht_name = ""
            try:
                de_name = de_dict[str(this_name_hash_id)].replace("'", "\\'")
            except KeyError:
                de_name = ""
            try:
                en_name = en_dict[str(this_name_hash_id)].replace("'", "\\'")
            except KeyError:
                en_name = ""
            try:
                es_name = es_dict[str(this_name_hash_id)].replace("'", "\\'")
            except KeyError:
                es_name = ""
            try:
                fr_name = fr_dict[str(this_name_hash_id)].replace("'", "\\'")
            except KeyError:
                fr_name = ""
            try:
                id_name = id_dict[str(this_name_hash_id)].replace("'", "\\'")
            except KeyError:
                id_name = ""
            try:
                jp_name = jp_dict[str(this_name_hash_id)].replace("'", "\\'")
            except KeyError:
                jp_name = ""
            try:
                kr_name = kr_dict[str(this_name_hash_id)].replace("'", "\\'")
            except KeyError:
                kr_name = ""
            try:
                pt_name = pt_dict[str(this_name_hash_id)].replace("'", "\\'")
            except KeyError:
                pt_name = ""
            try:
                ru_name = ru_dict[str(this_name_hash_id)].replace("'", "\\'")
            except KeyError:
                ru_name = ""
            try:
                th_name = th_dict[str(this_name_hash_id)].replace("'", "\\'")
            except KeyError:
                th_name = ""
            try:
                vi_name = vi_dict[str(this_name_hash_id)].replace("'", "\\'")
            except KeyError:
                vi_name = ""
            lang_dict = {
                "chs": chs_name,
                "cht": cht_name,
                "de": de_name,
                "en": en_name,
                "es": es_name,
                "fr": fr_name,
                "id": id_name,
                "jp": jp_name,
                "kr": kr_name,
                "pt": pt_name,
                "ru": ru_name,
                "th": th_name,
                "vi": vi_name
            }

            sql1 = r"INSERT INTO i18n_dict (item_id, chs, cht, de, en, es, fr, id, jp, kr, pt, ru, th, vi) VALUES" \
                   r" (%s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
                       this_item_id, chs_name, cht_name,
                       de_name, en_name, es_name, fr_name, id_name,
                       jp_name, kr_name, pt_name, ru_name,
                       th_name, vi_name)
            db.execute(sql1)

            for key_name in lang_dict.keys():
                if lang_dict[key_name] != "":
                    sql2 = r"INSERT INTO generic_dict (item_id, text, lang) VALUES (%s, '%s', '%s')" % (
                        this_item_id, lang_dict[key_name], key_name)
                    db.execute(sql2)

    for language in ACCEPTED_LANGUAGES:
        make_language_dict_json(language)


@app.get("/refresh/{token}", tags=["refresh"])
async def refresh(token: str, background_tasks: BackgroundTasks):
    if token != TOKEN:
        raise HTTPException(status_code=403, detail="Token not accepted")
    background_tasks.add_task(force_refresh_local_data)
    return {"status": "Add background task successfully"}
