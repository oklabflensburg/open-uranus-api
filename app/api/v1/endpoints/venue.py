import json

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from shapely.wkb import loads

from decimal import Decimal
from typing import List

from geojson import Feature, FeatureCollection

from app.db.session import get_db

from app.models.user import User

from app.schemas.venue import VenueCreate
from app.schemas.venue_response import VenueResponse, VenueGeoJSONPoint
from app.schemas.venue_junk_response import VenueJunkResponse
from app.schemas.venue_bounds_response import VenueBoundsResponse

from app.services.auth import get_current_user

from app.db.repository.venue import (
    get_all_venues,
    get_venue_by_id,
    get_venue_stats,
    get_simple_venue_by_id,
    get_venues_within_bounds,
    get_venues_by_name_junk,
    add_venue,
    add_user_venue
)


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No venues found by query: {query}'
        )

    return venue


@router.get('/{venue_id}', response_model=VenueResponse)
async def fetch_venue_by_id(
    venue_id: int,
    db: AsyncSession = Depends(get_db)
):
    venue = await get_venue_by_id(db, venue_id)

    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No venue found for venue_id: {venue_id}'
        )

    return venue


@router.get('/bounds', response_model=VenueBoundsResponse)
async def fetch_venues_within_bounds(
    xmin: Decimal,
    ymin: Decimal,
    xmax: Decimal,
    ymax: Decimal,
    db: AsyncSession = Depends(get_db)
):
    rows = await get_venues_within_bounds(db, xmin, ymin, xmax, ymax)

    if len(rows) < 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No venues found for bounds xmin: {xmin}, ymin; {ymin}, xmax: {xmax}, ymax: {ymax}')

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
    venue_data: VenueCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    new_venue = await add_venue(db, venue_data)
    await add_user_venue(db, current_user.id, new_venue.id, 1)

    geom = loads(bytes(new_venue.wkb_geometry.data))
    geojson = VenueGeoJSONPoint(type='Point', coordinates=[geom.x, geom.y])

    return VenueResponse(
        venue_id=new_venue.id,
        venue_organizer_id=new_venue.organizer_id,
        venue_name=new_venue.name,
        venue_street=new_venue.street,
        venue_house_number=new_venue.house_number,
        venue_postal_code=new_venue.postal_code,
        venue_city=new_venue.city,
        opened_at=new_venue.opened_at,
        closed_at=new_venue.closed_at,
        geojson=geojson
    )


@router.put('/{venue_id}', response_model=VenueResponse)
async def update_venue(
    venue_id: int,
    venue_update: VenueCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    FIELD_MAPPING = {
        'venue_organizer_id': 'organizer_id',
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No venue found for venue_id: {venue_id}'
        )

    update_data = venue_update.dict(exclude_unset=True)

    for old_field, new_field in FIELD_MAPPING.items():
        if old_field in update_data:
            setattr(venue, new_field, update_data[old_field])

    await db.commit()
    await db.refresh(venue)

    # Convert geometry to GeoJSON format
    geom = loads(bytes(venue.wkb_geometry.data))
    geojson = VenueGeoJSONPoint(type='Point', coordinates=[geom.x, geom.y])

    return VenueResponse(
        venue_id=venue.id,
        venue_organizer_id=venue.organizer_id,
        venue_name=venue.name,
        venue_street=venue.street,
        venue_house_number=venue.house_number,
        venue_postal_code=venue.postal_code,
        venue_city=venue.city,
        venue_opened_at=venue.opened_at,
        venue_closed_at=venue.closed_at,
        geojson=geojson
    )


@router.delete('/{venue_id}', response_model=dict)
async def delete_venue_by_id(
    venue_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    venue = await get_simple_venue_by_id(db, venue_id)

    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No venue found for venue_id: {venue_id}'
        )

    await db.delete(venue)
    await db.commit()

    return {'message': 'Venue deleted successfully'}


@router.get('/{venue_id}/stats', response_model=dict)
async def fetch_venue_stats(
    venue_id: int,
    db: AsyncSession = Depends(get_db)
):
    stats = await get_venue_stats(db, venue_id)

    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No stats found for venue_id: {venue_id}'
        )

    return stats
