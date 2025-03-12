from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone



class I18nLocaleBase(SQLModel):
    iso_639_1: str = Field(max_length=2, unique=True, nullable=False)
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: Optional[datetime] = None



class I18nLocale(I18nLocaleBase, table=True):
    __tablename__ = 'i18n_locale'
    __table_args__ = {'schema': 'uranus'}

    id: Optional[int] = Field(default=None, primary_key=True)
