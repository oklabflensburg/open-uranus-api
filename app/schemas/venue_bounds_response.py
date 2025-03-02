from pydantic import BaseModel, Field
from typing import List, Literal



class VenuePointGeometry(BaseModel):
    type: Literal['Point']
    coordinates: List[float]



class VenueFeatureProperties(BaseModel):
    label: str 



class VenueFeature(BaseModel):
    type: Literal['Feature']
    id: int 
    geometry: VenuePointGeometry
    properties: VenueFeatureProperties



class VenueBoundsResponse(BaseModel):
    type: Literal['FeatureCollection']
    features: List[VenueFeature]