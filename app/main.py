from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.v1.endpoints import (
    user,
    user_role,
    venue,
    organizer,
    event,
    space,
    space_type,
    venue_type,
    event_type,
    genre_type,
    license_type,
    image_type,
    i18n_locale
)
from app.core.config import settings


ALLOWED_EXTENSIONS = settings.ALLOWED_EXTENSIONS
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(
    docs_url='/docs',
    redoc_url=None,
    title='Veranstaltungen finden',
    summary='Diese Anwendung befindet sich noch in Entwicklung, bitte nutze diese API mit diesem Wissen.',
    version='0.2.2'
)

app.mount('/uploads', StaticFiles(directory=UPLOAD_DIR), name='uploads')


app.include_router(user.router, prefix='/user', tags=['User'])
app.include_router(user_role.router, prefix='/user/role', tags=['User roles'])
app.include_router(venue.router, prefix='/venue', tags=['Venue'])
app.include_router(venue_type.router, prefix='/venue/type', tags=['Venue'])
app.include_router(organizer.router, prefix='/organizer', tags=['Organizer'])
app.include_router(event.router, prefix='/event', tags=['Event'])
app.include_router(event_type.router, prefix='/event/type', tags=['Event'])
app.include_router(space.router, prefix='/space', tags=['Venue Space'])
app.include_router(space_type.router, prefix='/space/type', tags=['Venue Space'])
app.include_router(genre_type.router, prefix='/genre/type', tags=['Genre'])
app.include_router(license_type.router, prefix='/license/type', tags=['License'])
app.include_router(image_type.router, prefix='/image/type', tags=['Image'])
app.include_router(image_type.router, prefix='/image/type', tags=['Image'])
app.include_router(i18n_locale.router, prefix='/locale/type', tags=['Locale'])