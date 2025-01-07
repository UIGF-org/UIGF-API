from pydantic import BaseModel, field_validator
from typing import Optional, Any, Literal
from api_config import ACCEPTED_LANGUAGES


# ------------------------------------------------------------------------
# Pydantic Schemas for Requests/Responses
# ------------------------------------------------------------------------
class TranslateRequest(BaseModel):
    type: Literal["reverse", "normal"]
    lang: Literal[*ACCEPTED_LANGUAGES]
    game: Literal["genshin", "starrail", "zzz"]
    item_name: Optional[str] = None
    item_id: Optional[str] = None


class TranslateResponse(BaseModel):
    item_id: Optional[Any] = None
    item_name: Optional[Any] = None

    @field_validator("item_name", mode="before")
    def process_item_name(cls, value):
        if value is not None and isinstance(value, str):
            return value.replace("\\'", "'")
        return value
