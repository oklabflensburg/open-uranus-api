from fastapi import FastAPI
from app.api.v1.endpoints import venue, event, space



app = FastAPI(title='Uranus Venue Map')

app.include_router(venue.router, prefix='/venue', tags=['Veranstaltungsorte'])
app.include_router(event.router, prefix='/event', tags=['Veranstaltungen'])
app.include_router(space.router, prefix='/space', tags=['Veranstaltungens Räume'])
