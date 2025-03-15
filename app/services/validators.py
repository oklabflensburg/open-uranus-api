from fastapi import HTTPException, status, UploadFile
from PIL import Image

from app.core.config import settings



def validate_positive_int64(value: int) -> int:
    if value < 0 or value > 9223372036854775807:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Value must be a positive int64.',
        )

    return value



def validate_positive_int32(value: int) -> int:
    if value < 0 or value > 2147483647:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Value must be a positive int32.',
        )

    return value



def validate_positive_smallint(value: int) -> int:
    if value < 0 or value > 32767:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Value must be a positive smallint.',
        )

    return value



def validate_not_none(value):
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'{value} must not be None.',
        )

    return value



def validate_image(file: UploadFile):
    ext = file.filename.split('.')[-1].lower()

    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail='Invalid file type')

    try:
        Image.open(file.file).verify()
        file.file.seek(0)
    except Exception:
        raise HTTPException(status_code=400, detail='Corrupted image file')

    return ext