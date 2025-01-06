from .mysql_db import Base
from sqlalchemy import Column, Integer, String

# ------------------------------------------------------------------------
# MODEL DECLARATIONS
# ------------------------------------------------------------------------


class I18nDict(Base):
    """
    Reflects the i18n_dict table with the following columns:
    game_id, item_id, chs_text, cht_text, de_text, en_text, es_text,
    fr_text, id_text, jp_text, kr_text, pt_text, ru_text, th_text, vi_text
    """
    __tablename__ = "i18n_dict"

    # auto increment primary key if you want
    game_id = Column(Integer, index=True, nullable=False)
    item_id = Column(String(255), index=True, nullable=False, primary_key=True)

    chs_text = Column(String(255), default="")
    cht_text = Column(String(255), default="")
    de_text = Column(String(255), default="")
    en_text = Column(String(255), default="")
    es_text = Column(String(255), default="")
    fr_text = Column(String(255), default="")
    id_text = Column(String(255), default="")
    jp_text = Column(String(255), default="")
    kr_text = Column(String(255), default="")
    pt_text = Column(String(255), default="")
    ru_text = Column(String(255), default="")
    th_text = Column(String(255), default="")
    vi_text = Column(String(255), default="")
