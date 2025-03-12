from pydantic import BaseModel



class I18nLocaleResponse(BaseModel):
    locale_id: int
    locale_code: str
    locale_name: str