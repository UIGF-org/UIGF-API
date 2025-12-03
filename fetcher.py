import httpx
import io
import json
import os
import zipfile
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

SNAP_METADATA_LANGS = ["CHS", "CHT", "DE", "EN", "ES", "FR", "ID", "IT", "JP", "KR", "PT", "RU", "TH", "TR", "VI"]
SNAP_METADATA_ZIP_URL = "https://github.com/DGP-Studio/Snap.Metadata/archive/refs/heads/main.zip"
SNAP_METADATA_ZIP_PREFIX = "Snap.Metadata-main"  # Folder name inside the zip


def _read_json_from_zip(zf: zipfile.ZipFile, path: str) -> dict | list | None:
    """Read and parse a JSON file from the zip archive."""
    try:
        with zf.open(path) as f:
            return json.load(f)
    except (KeyError, json.JSONDecodeError) as e:
        logger.error(f"Failed to read {path} from zip: {e}")
        return None


def fetch_genshin_impact_update():
    """
    Fetch Genshin Impact item data from Snap.Metadata.
    
    Optimization strategy:
    - Download the entire repository as a ZIP file (1 HTTP request)
    - Extract and process files in memory
    
    This reduces ~1600+ HTTP requests to just 1 request + local I/O operations.
    """
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN is not set in environment variables")
    
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    
    # Step 1: Download the repository ZIP file
    logger.info("Downloading Snap.Metadata repository ZIP...")
    with httpx.Client(headers=headers, timeout=120.0, follow_redirects=True) as client:
        resp = client.get(SNAP_METADATA_ZIP_URL)
        resp.raise_for_status()
        zip_data = resp.content
    
    logger.info(f"Downloaded ZIP file: {len(zip_data) / 1024 / 1024:.2f} MB")
    
    # Step 2: Open ZIP in memory and extract data
    id_to_name: dict[str, dict[int, str]] = {}
    
    with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zf:
        # Get avatar IDs from CHS Meta.json
        meta_path = f"{SNAP_METADATA_ZIP_PREFIX}/Genshin/CHS/Meta.json"
        meta_data = _read_json_from_zip(zf, meta_path)
        
        if not meta_data:
            raise RuntimeError("Failed to read Meta.json from ZIP")
        
        avatar_ids = [
            key.split("/")[1] 
            for key in meta_data.keys() 
            if key.startswith("Avatar/")
        ]
        logger.info(f"Found {len(avatar_ids)} avatar IDs from Meta.json")
        
        # Process each language
        for lang in SNAP_METADATA_LANGS:
            this_lang_id_to_name: dict[int, str] = {}
            
            # Read Weapon.json
            weapon_path = f"{SNAP_METADATA_ZIP_PREFIX}/Genshin/{lang}/Weapon.json"
            weapon_data = _read_json_from_zip(zf, weapon_path)
            if weapon_data:
                for weapon in weapon_data:
                    weapon_name = weapon.get("Name", "")
                    weapon_id = weapon.get("Id", 0)
                    if weapon_name and weapon_id:
                        this_lang_id_to_name[weapon_id] = weapon_name
            
            # Read each Avatar file
            for avatar_id in avatar_ids:
                avatar_path = f"{SNAP_METADATA_ZIP_PREFIX}/Genshin/{lang}/Avatar/{avatar_id}.json"
                avatar_data = _read_json_from_zip(zf, avatar_path)
                if avatar_data:
                    avatar_name = avatar_data.get("Name", "")
                    avatar_id_int = avatar_data.get("Id", 0)
                    if avatar_name and avatar_id_int:
                        this_lang_id_to_name[avatar_id_int] = avatar_name
            
            id_to_name[lang] = this_lang_id_to_name
            logger.debug(f"Processed {lang}: {len(this_lang_id_to_name)} items")
    
    # Step 3: Build response
    all_item_ids = id_to_name["CHS"].keys()
    logger.info(f"Fetched total {len(all_item_ids)} unique item IDs from Genshin Impact Snap.Metadata")
    
    resp = {}
    for item_id in all_item_ids:
        if item_id in DEPRECATED_ID:
            logger.warning(f"Item ID {item_id} is deprecated, skipping...")
            continue
        lang_dict = {}
        for lang in SNAP_METADATA_LANGS:
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
