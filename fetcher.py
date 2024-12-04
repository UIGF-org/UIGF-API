import requests
import json
import os


def fetch_genshin_impact_update():
    target_host = "https://raw.githubusercontent.com/Masterain98/GenshinData/main/"
    avatar_config_file = "AvatarExcelConfigData.json"
    weapon_config_file = "WeaponExcelConfigData.json"
    resp = {}

    avatar_excel_config_data = json.loads(requests.get(target_host + avatar_config_file).text)
    weapon_excel_config_data = json.loads(requests.get(target_host + weapon_config_file).text)
    chs_dict = json.loads(requests.get(target_host + "TextMap/TextMapCHS.json").text)
    cht_dict = json.loads(requests.get(target_host + "TextMap/TextMapCHT.json").text)
    de_dict = json.loads(requests.get(target_host + "TextMap/TextMapDE.json").text)
    en_dict = json.loads(requests.get(target_host + "TextMap/TextMapEN.json").text)
    es_dict = json.loads(requests.get(target_host + "TextMap/TextMapES.json").text)
    fr_dict = json.loads(requests.get(target_host + "TextMap/TextMapFR.json").text)
    id_dict = json.loads(requests.get(target_host + "TextMap/TextMapID.json").text)
    jp_dict = json.loads(requests.get(target_host + "TextMap/TextMapJP.json").text)
    kr_dict = json.loads(requests.get(target_host + "TextMap/TextMapKR.json").text)
    pt_dict = json.loads(requests.get(target_host + "TextMap/TextMapPT.json").text)
    ru_dict = json.loads(requests.get(target_host + "TextMap/TextMapRU.json").text)
    th_dict = json.loads(requests.get(target_host + "TextMap/TextMapTH.json").text)
    vi_dict = json.loads(requests.get(target_host + "TextMap/TextMapVI.json").text)
    dict_list = [chs_dict, cht_dict, de_dict, en_dict, es_dict, fr_dict, id_dict,
                 jp_dict, kr_dict, pt_dict, ru_dict, th_dict, vi_dict]
    item_list = avatar_excel_config_data + weapon_excel_config_data

    try:
        for file in os.listdir("dict/genshin"):
            os.remove("dict/genshin/" + file)
    except FileNotFoundError:
        pass

    # Item list has weapon list and character list
    for item in item_list:
        this_name_hash_id = str(item["NameTextMapHash"])
        this_item_id = int(item["id"])
        name_list = [
            lang_dict[this_name_hash_id].replace("'", "\\'") if this_name_hash_id in lang_dict.keys() else "" for
            lang_dict in dict_list
        ]
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
        resp[this_item_id] = lang_dict
    return resp


def fetch_starrail_update():
    target_host = "https://gitlab.com/Dimbreath/turnbasedgamedata/-/raw/main/"
    avatar_config_file = "ExcelOutput/AvatarConfig.json"
    weapon_config_file = "ExcelOutput/EquipmentConfig.json"
    resp = {}

    avatar_config_data = json.loads(requests.get(target_host + avatar_config_file).text)
    weapon_config_data = json.loads(requests.get(target_host + weapon_config_file).text)
    chs_dict = json.loads(requests.get(target_host + "TextMap/TextMapCHS.json").text)
    cht_dict = json.loads(requests.get(target_host + "TextMap/TextMapCHT.json").text)
    de_dict = json.loads(requests.get(target_host + "TextMap/TextMapDE.json").text)
    en_dict = json.loads(requests.get(target_host + "TextMap/TextMapEN.json").text)
    es_dict = json.loads(requests.get(target_host + "TextMap/TextMapES.json").text)
    fr_dict = json.loads(requests.get(target_host + "TextMap/TextMapFR.json").text)
    id_dict = json.loads(requests.get(target_host + "TextMap/TextMapID.json").text)
    jp_dict = json.loads(requests.get(target_host + "TextMap/TextMapJP.json").text)
    kr_dict = json.loads(requests.get(target_host + "TextMap/TextMapKR.json").text)
    pt_dict = json.loads(requests.get(target_host + "TextMap/TextMapPT.json").text)
    ru_dict = json.loads(requests.get(target_host + "TextMap/TextMapRU.json").text)
    th_dict = json.loads(requests.get(target_host + "TextMap/TextMapTH.json").text)
    vi_dict = json.loads(requests.get(target_host + "TextMap/TextMapVI.json").text)
    dict_list = [chs_dict, cht_dict, de_dict, en_dict, es_dict, fr_dict, id_dict,
                 jp_dict, kr_dict, pt_dict, ru_dict, th_dict, vi_dict]
    item_list = avatar_config_data + weapon_config_data

    try:
        for file in os.listdir("dict/starrail"):
            os.remove("dict/starrail/" + file)
    except FileNotFoundError:
        pass

    for item in item_list:
        if "AvatarID" in item:
            this_name_hash_id = str(item["AvatarName"]["Hash"])
            this_item_id = int(item["AvatarID"])
        elif "EquipmentID" in item:
            this_name_hash_id = str(item["EquipmentName"]["Hash"])
            this_item_id = int(item["EquipmentID"])
        else:
            raise ValueError(f"Unknown item type: {item}")

        name_list = [
            lang_dict[this_name_hash_id].replace("'", "\\'") if this_name_hash_id in lang_dict.keys() else "" for
            lang_dict in dict_list
        ]
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
        resp[this_item_id] = lang_dict
    return resp


def fetch_zzz_update():
    target_host = "https://git.mero.moe/dimbreath/ZenlessData/raw/branch/master/"
    avatar_config_file = "FileCfg/AvatarBaseTemplateTb.json"  # agent
    weapon_config_file = "FileCfg/ItemTemplateTb.json"  # w-engine and bangboo
    resp = {}

    avatar_config_data = json.loads(requests.get(target_host + avatar_config_file).text)["PEPPKLMFFBD"]
    weapon_config_data = json.loads(requests.get(target_host + weapon_config_file).text)["PEPPKLMFFBD"]
    print(f"Successfully fetched {len(avatar_config_data) + len(weapon_config_data)} items from zzz")
    chs_dict = json.loads(requests.get(target_host + "TextMap/TextMapTemplateTb.json").text)
    cht_dict = json.loads(requests.get(target_host + "TextMap/TextMap_CHTTemplateTb.json").text)
    de_dict = json.loads(requests.get(target_host + "TextMap/TextMap_DETemplateTb.json").text)
    en_dict = json.loads(requests.get(target_host + "TextMap/TextMap_ENTemplateTb.json").text)
    es_dict = json.loads(requests.get(target_host + "TextMap/TextMap_ESTemplateTb.json").text)
    fr_dict = json.loads(requests.get(target_host + "TextMap/TextMap_FRTemplateTb.json").text)
    id_dict = json.loads(requests.get(target_host + "TextMap/TextMap_IDTemplateTb.json").text)
    jp_dict = json.loads(requests.get(target_host + "TextMap/TextMap_JATemplateTb.json").text)
    kr_dict = json.loads(requests.get(target_host + "TextMap/TextMap_KOTemplateTb.json").text)
    pt_dict = json.loads(requests.get(target_host + "TextMap/TextMap_PTTemplateTb.json").text)
    ru_dict = json.loads(requests.get(target_host + "TextMap/TextMap_RUTemplateTb.json").text)
    th_dict = json.loads(requests.get(target_host + "TextMap/TextMap_THTemplateTb.json").text)
    vi_dict = json.loads(requests.get(target_host + "TextMap/TextMap_VITemplateTb.json").text)
    print(f"Successfully fetched 13 language dictionaries from zzz")
    dict_list = [chs_dict, cht_dict, de_dict, en_dict, es_dict, fr_dict, id_dict,
                 jp_dict, kr_dict, pt_dict, ru_dict, th_dict, vi_dict]
    item_list = avatar_config_data + weapon_config_data
    print(f"Successfully fetched {len(item_list)} items from zzz")

    try:
        for file in os.listdir("dict/zzz"):
            os.remove("dict/zzz/" + file)
    except FileNotFoundError:
        pass

    for item in item_list:
        print(f"Processing item {item}")
        this_name_hash_id = item["FJECNNMMDGH"]
        this_item_id = item["GKNMDKNIMHP"]
        name_list = [
            lang_dict[this_name_hash_id].replace("'", "\\'") if this_name_hash_id in lang_dict.keys() else "" for
            lang_dict in dict_list
        ]
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
        resp[this_item_id] = lang_dict
    print(f"Returning {len(resp)} items")
    return resp