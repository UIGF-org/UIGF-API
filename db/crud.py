from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import json
import redis
from db.models import I18nDict
from typing import Dict, Optional
from base_logger import logger
from api_config import game_name_id_map


def get_game_id_by_name(this_game_name: str) -> Optional[int]:
    return game_name_id_map.get(this_game_name)


def get_lang_column(lang: str):
    """
    Map from short-code to I18nDict property.
    """
    mapper = {
        "chs": I18nDict.chs_text,
        "cht": I18nDict.cht_text,
        "de": I18nDict.de_text,
        "en": I18nDict.en_text,
        "es": I18nDict.es_text,
        "fr": I18nDict.fr_text,
        "id": I18nDict.id_text,
        "jp": I18nDict.jp_text,
        "kr": I18nDict.kr_text,
        "pt": I18nDict.pt_text,
        "ru": I18nDict.ru_text,
        "th": I18nDict.th_text,
        "vi": I18nDict.vi_text,
    }
    return mapper.get(lang)


def clear_game_data(db: Session, game_id: int):
    """ Delete old data from i18n_dict for a given game_id. """
    try:
        db.query(I18nDict).filter(I18nDict.game_id == game_id).delete()
        db.commit()
    except SQLAlchemyError as e:
        logger.error(f"Error clearing game data: {e}")
        db.rollback()
        raise RuntimeError("Error clearing game data")


def insert_localization_data(db: Session, redis_client: redis.Redis, game_id: int,
                             localization_dict: Dict[str, Dict[str, str]]):
    """
    Insert data into i18n_dict
    localization_dict = { item_id: { 'en': 'some text', 'chs': '中文', ...}, ... }
    """
    i18n_entries = []

    # Gather all rows in memory
    for item_id, translation in localization_dict.items():
        i18n_entry = I18nDict(
            game_id=game_id,
            item_id=item_id,
            chs_text=translation.get("chs", ""),
            cht_text=translation.get("cht", ""),
            de_text=translation.get("de", ""),
            en_text=translation.get("en", ""),
            es_text=translation.get("es", ""),
            fr_text=translation.get("fr", ""),
            id_text=translation.get("id", ""),
            jp_text=translation.get("jp", ""),
            kr_text=translation.get("kr", ""),
            pt_text=translation.get("pt", ""),
            ru_text=translation.get("ru", ""),
            th_text=translation.get("th", ""),
            vi_text=translation.get("vi", "")
        )
        i18n_entries.append(i18n_entry)

    for entry in i18n_entries:
        try:
            db.add(entry)
            db.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error inserting localization data: {e}")
            db.rollback()
            raise RuntimeError("Error inserting localization data")
    logger.info(f"Inserted {len(i18n_entries)} rows into i18n_dict, task finished.")

    pipe = redis_client.pipeline(transaction=False)
    for entry in i18n_entries:
        data_dict = {
            "chs_text": entry.chs_text,
            "cht_text": entry.cht_text,
            "de_text": entry.de_text,
            "en_text": entry.en_text,
            "es_text": entry.es_text,
            "fr_text": entry.fr_text,
            "id_text": entry.id_text,
            "jp_text": entry.jp_text,
            "kr_text": entry.kr_text,
            "pt_text": entry.pt_text,
            "ru_text": entry.ru_text,
            "th_text": entry.th_text,
            "vi_text": entry.vi_text,
        }
        redis_key = f"uigf:game-{entry.game_id}:{entry.item_id}"
        pipe.set(redis_key, json.dumps(data_dict, ensure_ascii=False))

    pipe.execute()
    logger.info("All inserted items have been cached in Redis.")
