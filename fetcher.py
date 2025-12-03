import httpx
import json
import os
from base_logger import logger


DEPRECATED_GENSHIN_ID = {
    11506: "磐岩结绿",
    11507: "凭虚",
    12505: "砥厄鱼",
    12506: "异史",
    13506: "弦主",
    15504: "阳龙之梦",
    15505: "悬黎干钩",
    15506: "破镜",
    12304: "石英大剑",
    14306: "琉珀玦",
    15306: "黑檀弓",
    13304: "「旷怨」",
    11419: "「一心传」名刀 × 3",
    11420: "「一心传」名刀 × 3",
    11421: "「一心传」名刀 × 3",
    11429: "水仙十字之剑",
}
DEPRECATED_ID = set(DEPRECATED_GENSHIN_ID.keys())

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def fetch_genshin_impact_update():
    if GITHUB_TOKEN:
        headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
        gh_client = httpx.Client(headers=headers)
    else:
        raise ValueError("GITHUB_TOKEN is not set in environment variables")
    snap_metadata_lang = ["CHS", "CHT", "DE", "EN", "ES", "FR", "ID", "IT", "JP", "KR", "PT", "RU", "TH", "TR", "VI"]
    target_host = "https://raw.githubusercontent.com/DGP-Studio/Snap.Metadata/main"
    name_to_id = {}
    id_to_name = {}
    resp = {}
    for lang in snap_metadata_lang:
        this_lang_name_to_id = {}
        this_lang_id_to_name = {}
        # Weapon
        weapon_config_file = f"{target_host}/Genshin/{lang}/Weapon.json"
        weapon_data = gh_client.get(weapon_config_file).json()
        for weapon in weapon_data:
            this_weapon_name = weapon.get("Name", "")
            this_weapon_id = weapon.get("Id", 0)
            if this_weapon_name and this_weapon_id:
                this_lang_name_to_id[this_weapon_name] = this_weapon_id
                this_lang_id_to_name[this_weapon_id] = this_weapon_name

        # Character
        meta_file = f"{target_host}/Genshin/{lang}/Meta.json"
        meta_data = gh_client.get(meta_file).json()
        avatar_file_index = [index for index in meta_data.keys() if index.startswith("Avatar/")]
        for avtar_indx in avatar_file_index:
            avatar_file_url = f"{target_host}/Genshin/{lang}/{avtar_indx}.json"
            avatar_data = gh_client.get(avatar_file_url).json()
            avatar_name = avatar_data.get("Name", "")
            avatar_id = avatar_data.get("Id", 0)
            if avatar_name and avatar_id:
                this_lang_name_to_id[avatar_name] = avatar_id
                this_lang_id_to_name[avatar_id] = avatar_name

        name_to_id[lang] = this_lang_name_to_id
        id_to_name[lang] = this_lang_id_to_name

    all_item_ids = id_to_name["CHS"].keys()
    logger.info(f"Fetched total {len(all_item_ids)} unique item IDs from Genshin Impact Snap.Metadata")

    for item_id in all_item_ids:
        if item_id in DEPRECATED_ID:
            logger.warning(f"Item ID {item_id} is deprecated, skipping...")
            continue
        lang_dict = {}
        for lang in snap_metadata_lang:
            item_name = id_to_name[lang].get(item_id, "")
            lang_code = lang.lower()
            lang_dict[lang_code] = item_name
        resp[item_id] = lang_dict
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
            lang_dict[this_name_hash_id] if this_name_hash_id in lang_dict.keys() else "" for
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
            lang_dict[this_name_hash_id] if this_name_hash_id in lang_dict.keys() else "" for
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
