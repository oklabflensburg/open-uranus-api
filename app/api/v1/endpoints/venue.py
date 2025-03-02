from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from geojson import Feature, FeatureCollection, Point
from decimal import Decimal
from typing import List

import json

from app.db.session import get_db

from app.schemas.venue_response import VenueResponse
from app.schemas.venue_bounds_response import VenueBoundsResponse

from app.db.repository.venue import get_all_venues, get_venue_by_id, get_venues_within_bounds



router = APIRouter()

@router.get('/', response_model=List[VenueResponse])
async def fetch_all_venues(db: AsyncSession = Depends(get_db)):
    venues = await get_all_venues(db)

    return venues



@router.get('/id', response_model=List[VenueResponse])
async def fetch_venue_by_id(
    venue_id: int,
    db: AsyncSession = Depends(get_db)
):
    venues = await get_venue_by_id(db, venue_id)

    if len(venues) < 1:
        raise HTTPException(status_code=404, detail=f'No venue found for venue_id: {venue_id}')

    return venues



@router.get('/bounds', response_model=VenueBoundsResponse)
async def fetch_venues_within_bounds(
    xmin: Decimal, ymin: Decimal, xmax: Decimal, ymax: Decimal,
    db: AsyncSession = Depends(get_db)
):
    rows = await get_venues_within_bounds(db, xmin, ymin, xmax, ymax)

    if len(rows) < 1:
        raise HTTPException(status_code=404, detail=f'No venues found for bounds xmin: {xmin}, ymin; {ymin}, xmax: {xmax}, ymax: {ymax}')

    features = [
        Feature(
            id=row['id'],
            geometry=json.loads(row['geojson']),
            properties={'label': f'{row["name"]}'}
        )

        for row in rows
    ]

    venues = FeatureCollection(features)

    return venues
