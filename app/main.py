from fastapi import FastAPI
from app.api.v1.endpoints import venue, event, space, space_type, venue_type, genre_type



app = FastAPI(title='Uranus Venue Map')

app.include_router(venue.router, prefix='/venue', tags=['Veranstaltungsorte'])
app.include_router(venue_type.router, prefix='/venue/type', tags=['Veranstaltungsorte'])
app.include_router(event.router, prefix='/event', tags=['Veranstaltungen'])
app.include_router(space.router, prefix='/space', tags=['Veranstaltungsräume'])
app.include_router(space_type.router, prefix='/space/type', tags=['Veranstaltungsräume'])
app.include_router(genre_type.router, prefix='/genre/type', tags=['Genre'])
