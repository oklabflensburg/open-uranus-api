from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from geojson import Feature, FeatureCollection, Point
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from shapely.wkb import loads
from decimal import Decimal
from typing import List

import json

from app.db.session import get_db

from app.models.venue import Venue
from app.schemas.venue_create import VenueCreate
from app.schemas.venue_response import VenueResponse, VenueGeoJSONPoint
from app.schemas.venue_junk_response import VenueJunkResponse
from app.schemas.venue_bounds_response import VenueBoundsResponse

from app.db.repository.venue import get_all_venues, get_venue_by_id, get_simple_venue_by_id, get_venues_within_bounds, get_venues_by_name_junk



router = APIRouter()

@router.get('/', response_model=List[VenueResponse])
async def fetch_all_venues(db: AsyncSession = Depends(get_db)):
    venues = await get_all_venues(db)

    return venues



@router.get('/junk', response_model=List[VenueJunkResponse])
async def fetch_venues_by_name_junk(
    query: str,
    db: AsyncSession = Depends(get_db)
):
    venue = await get_venues_by_name_junk(db, query)

    if not venue:
        raise HTTPException(status_code=404, detail=f'No venue found for venue_id: {venue_id}')

    return venue



@router.get('/id', response_model=VenueResponse)
async def fetch_venue_by_id(
    venue_id: int,
    db: AsyncSession = Depends(get_db)
):
    venue = await get_venue_by_id(db, venue_id)

    if not venue:
        raise HTTPException(status_code=404, detail=f'No venue found for venue_id: {venue_id}')

    return venue



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
            properties={'label': f'{row['name']}'}
        )

        for row in rows
    ]

    venues = FeatureCollection(features)

    return venues


@router.post('/', response_model=VenueResponse)
async def create_venue(
        venue: VenueCreate,
        db: AsyncSession = Depends(get_db)
):
    point = from_shape(Point(venue.venue_longitude, venue.venue_latitude), srid=4326)
    new_venue = Venue(
        name=venue.venue_name,
        street=venue.venue_street,
        house_number=venue.venue_house_number,
        postal_code=venue.venue_postal_code,
        city=venue.venue_city,
        opened_at=venue.venue_opened_at,
        wkb_geometry=point
    )

    db.add(new_venue)

    await db.flush()
    await db.commit()
    await db.refresh(new_venue)

    geom = loads(bytes(new_venue.wkb_geometry.data))
    geojson = VenueGeoJSONPoint(type='Point', coordinates=[geom.x, geom.y])

    return VenueResponse(
        venue_id=new_venue.id,
        venue_name=new_venue.name,
        venue_street=new_venue.street,
        venue_house_number=new_venue.house_number,
        venue_postal_code=new_venue.postal_code,
        venue_city=new_venue.city,
        opened_at=new_venue.opened_at,
        closed_at=new_venue.closed_at,
        geojson=geojson
    )



@router.patch('/{venue_id}', response_model=VenueResponse)
async def update_venue(
    venue_id: int,
    venue_update: VenueCreate,
    db: AsyncSession = Depends(get_db),
):
    FIELD_MAPPING = {
        'venue_name': 'name',
        'venue_street': 'street',
        'venue_house_number': 'house_number',
        'venue_postal_code': 'postal_code',
        'venue_city': 'city',
        'venue_opened_at': 'opened_at',
        'venue_closed_at': 'closed_at'
    }

    venue = await get_simple_venue_by_id(db, venue_id)

    if not venue:
        raise HTTPException(status_code=404, detail=f'No venue found for venue_id: {venue_id}')

    update_data = venue_update.dict(exclude_unset=True)  # Get only provided fields

    for old_field, new_field in FIELD_MAPPING.items():
        if old_field in update_data:
            setattr(venue, new_field, update_data[old_field])  # Apply mapping

    await db.commit()
    await db.refresh(venue)  # Refresh the instance to reflect changes

    # Convert geometry to GeoJSON format
    geom = loads(bytes(venue.wkb_geometry.data))  # Convert WKB to Shapely object
    geojson = VenueGeoJSONPoint(type='Point', coordinates=[geom.x, geom.y])

    return VenueResponse(
        venue_id=venue.id,
        venue_name=venue.name,
        venue_street=venue.street,
        venue_house_number=venue.house_number,
        venue_postal_code=venue.postal_code,
        venue_city=venue.city,
        opened_at=venue.opened_at,
        closed_at=venue.closed_at,
        geojson=geojson
    )



@router.delete('/{venue_id}', response_model=dict)
async def delete_venue_by_id(
        venue_id: int,
        db: AsyncSession = Depends(get_db)
):
    venue = await get_simple_venue_by_id(db, venue_id)

    if not venue:
        raise HTTPException(status_code=404, detail=f'No venue found for venue_id: {venue_id}')

    await db.delete(venue)
    await db.commit()

    return {'message': 'Venue deleted successfully'}
