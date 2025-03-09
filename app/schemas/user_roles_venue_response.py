from pydantic import BaseModel



class UserRolesVenueResponse(BaseModel):
    user_id: int
    venue_id: int
    user_role_id: int
    venue_name: str
    is_organization_editor: bool
    is_venue_editor: bool
    is_space_editor: bool
    is_event_editor: bool
    is_venue_type_editor: bool
    is_space_type_editor: bool
    is_event_type_editor: bool
    is_genre_type_editor: bool
    is_image_type_editor: bool
    is_license_type_editor: bool