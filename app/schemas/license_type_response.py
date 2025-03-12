from pydantic import BaseModel



class LicenseTypeResponse(BaseModel):
    license_type_id: int
    license_type_name: str