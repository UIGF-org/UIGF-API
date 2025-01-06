import json
import logging
from sqlalchemy.orm import Session
from sqlalchemy import exc

from db.models import I18nDict, GenericDict
from typing import Dict, List, Optional
from api_config import game_name_id_map, ACCEPTED_LANGUAGES, LANGUAGE_PAIRS


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
    """ Delete old data from i18n_dict & generic_dict for a given game_id. """
    db.query(I18nDict).filter(I18nDict.game_id == game_id).delete()
    db.query(GenericDict).filter(GenericDict.game_id == game_id).delete()
    db.commit()


def insert_localization_data(
        db: Session,
        game_id: int,
        localization_dict: Dict[str, Dict[str, str]]
):
    """
    Insert data into i18n_dict & generic_dict.
    localization_dict = { item_id: { 'en': 'some text', 'chs': '中文', ...}, ... }
    """
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
        db.add(i18n_entry)

        # Insert into GenericDict
        for lang_code, text_value in translation.items():
            if text_value:
                gdict = GenericDict(
                    game_id=game_id,
                    item_id=item_id,
                    text=text_value,  # Properly set "text"
                    lang=lang_code  # And "lang"
                )
                db.add(gdict)

    db.commit()
