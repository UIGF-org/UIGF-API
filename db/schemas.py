from pydantic import BaseModel
from typing import Optional, Any


# ------------------------------------------------------------------------
# Pydantic Schemas for Requests/Responses
# ------------------------------------------------------------------------
class TranslateRequest(BaseModel):
    type: str
    lang: str
    game: str
    item_name: Optional[str] = None
    item_id: Optional[str] = None


class TranslateResponse(BaseModel):
    item_id: Optional[Any] = None
    item_name: Optional[Any] = None