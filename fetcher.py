import httpx
import json
import os
from base_logger import logger


def fetch_genshin_impact_update():
    target_host = "https://raw.githubusercontent.com/Masterain98/GenshinData/main/"
    avatar_config_file = "AvatarExcelConfigData.json"
    weapon_config_file = "WeaponExcelConfigData.json"
    resp = {}

    avatar_excel_config_data = json.loads(httpx.get(target_host + avatar_config_file).text)
    weapon_excel_config_data = json.loads(httpx.get(target_host + weapon_config_file).text)
    chs_dict = json.loads(httpx.get(target_host + "TextMap/TextMapCHS.json").text)
    cht_dict = json.loads(httpx.get(target_host + "TextMap/TextMapCHT.json").text)
    de_dict = json.loads(httpx.get(target_host + "TextMap/TextMapDE.json").text)
    en_dict = json.loads(httpx.get(target_host + "TextMap/TextMapEN.json").text)
    es_dict = json.loads(httpx.get(target_host + "TextMap/TextMapES.json").text)
    fr_dict = json.loads(httpx.get(target_host + "TextMap/TextMapFR.json").text)
    id_dict = json.loads(httpx.get(target_host + "TextMap/TextMapID.json").text)
    jp_dict = json.loads(httpx.get(target_host + "TextMap/TextMapJP.json").text)
    kr_dict = json.loads(httpx.get(target_host + "TextMap/TextMapKR.json").text)
    pt_dict = json.loads(httpx.get(target_host + "TextMap/TextMapPT.json").text)
    ru_dict = json.loads(httpx.get(target_host + "TextMap/TextMapRU.json").text)
    th_dict = json.loads(httpx.get(target_host + "TextMap/TextMapTH.json").text)
    vi_dict = json.loads(httpx.get(target_host + "TextMap/TextMapVI.json").text)
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

    avatar_config_data = json.loads(httpx.get(target_host + avatar_config_file).text)
    weapon_config_data = json.loads(httpx.get(target_host + weapon_config_file).text)
    chs_dict = json.loads(httpx.get(target_host + "TextMap/TextMapCHS.json").text)
    cht_dict = json.loads(httpx.get(target_host + "TextMap/TextMapCHT.json").text)
    de_dict = json.loads(httpx.get(target_host + "TextMap/TextMapDE.json").text)
    en_dict = json.loads(httpx.get(target_host + "TextMap/TextMapEN.json").text)
    es_dict = json.loads(httpx.get(target_host + "TextMap/TextMapES.json").text)
    fr_dict = json.loads(httpx.get(target_host + "TextMap/TextMapFR.json").text)
    id_dict = json.loads(httpx.get(target_host + "TextMap/TextMapID.json").text)
    jp_dict = json.loads(httpx.get(target_host + "TextMap/TextMapJP.json").text)
    kr_dict = json.loads(httpx.get(target_host + "TextMap/TextMapKR.json").text)
    pt_dict = json.loads(httpx.get(target_host + "TextMap/TextMapPT.json").text)
    ru_dict = json.loads(httpx.get(target_host + "TextMap/TextMapRU.json").text)
    th_dict = json.loads(httpx.get(target_host + "TextMap/TextMapTH.json").text)
    vi_dict = json.loads(httpx.get(target_host + "TextMap/TextMapVI.json").text)
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

    name_hash_id = ""
    item_id = ""

    avatar_config_data = json.loads(httpx.get(target_host + avatar_config_file).text)
    key_name = list(avatar_config_data.keys())
    if len(key_name) == 1:
        avatar_config_data = avatar_config_data[key_name[0]]
        for k, v in avatar_config_data[0].items():
            if v == "Avatar_Female_Size02_Anbi":
                name_hash_id = k
            if v == 1011:
                item_id = k
    if name_hash_id == "" or item_id == "":
        raise ValueError("Failed to fetch name_hash_id and item_id")
    else:
        logger.info(f"Successfully fetched name_hash_id: [{name_hash_id}] and item_id: [{item_id}] from zzz")

    weapon_config_data = json.loads(httpx.get(target_host + weapon_config_file).text)
    key_name = list(weapon_config_data.keys())
    if len(key_name) == 1:
        weapon_config_data = weapon_config_data[key_name[0]]

    # filter weapon items
    def is_valid_weapon_item(name_hash_value: str):
        if name_hash_value.startswith("Bangboo_Name_"):
            return True
        if name_hash_value.startswith("Item_Weapon_"):
            return True
        return False
    weapon_config_data = list(filter(lambda x: is_valid_weapon_item(x[name_hash_id]), weapon_config_data))

    logger.info(f"Successfully fetched {len(avatar_config_data)} avatar items + {len(weapon_config_data)} weapon items from zzz")
    chs_dict = json.loads(httpx.get(target_host + "TextMap/TextMapTemplateTb.json").text)
    cht_dict = json.loads(httpx.get(target_host + "TextMap/TextMap_CHTTemplateTb.json").text)
    de_dict = json.loads(httpx.get(target_host + "TextMap/TextMap_DETemplateTb.json").text)
    en_dict = json.loads(httpx.get(target_host + "TextMap/TextMap_ENTemplateTb.json").text)
    es_dict = json.loads(httpx.get(target_host + "TextMap/TextMap_ESTemplateTb.json").text)
    fr_dict = json.loads(httpx.get(target_host + "TextMap/TextMap_FRTemplateTb.json").text)
    id_dict = json.loads(httpx.get(target_host + "TextMap/TextMap_IDTemplateTb.json").text)
    jp_dict = json.loads(httpx.get(target_host + "TextMap/TextMap_JATemplateTb.json").text)
    kr_dict = json.loads(httpx.get(target_host + "TextMap/TextMap_KOTemplateTb.json").text)
    pt_dict = json.loads(httpx.get(target_host + "TextMap/TextMap_PTTemplateTb.json").text)
    ru_dict = json.loads(httpx.get(target_host + "TextMap/TextMap_RUTemplateTb.json").text)
    th_dict = json.loads(httpx.get(target_host + "TextMap/TextMap_THTemplateTb.json").text)
    vi_dict = json.loads(httpx.get(target_host + "TextMap/TextMap_VITemplateTb.json").text)
    dict_list = [chs_dict, cht_dict, de_dict, en_dict, es_dict, fr_dict, id_dict,
                 jp_dict, kr_dict, pt_dict, ru_dict, th_dict, vi_dict]
    item_list = avatar_config_data + weapon_config_data
    logger.info(f"Successfully fetched {len(item_list)} items from zzz")

    try:
        for file in os.listdir("dict/zzz"):
            os.remove("dict/zzz/" + file)
    except FileNotFoundError:
        pass

    for item in item_list:
        this_name_hash_id = item[name_hash_id]
        this_item_id = item[item_id]
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
