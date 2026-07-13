import secrets
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from ..config import settings
from ..deps import require_roles
from ..models import User, UserRole
from ..schemas import MediaUploadOut

router = APIRouter(prefix="/media", tags=["media"])

editor_only = require_roles(UserRole.SUPERADMIN, UserRole.TRAINING_COORDINATOR)

UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "image/svg+xml": ".svg",
}
MAX_BYTES = 8 * 1024 * 1024  # 8 МБ


@router.post("/image", response_model=MediaUploadOut)
async def upload_image(
    file: UploadFile = File(...),
    _: User = Depends(editor_only),
):
    ext = ALLOWED.get(file.content_type)
    if ext is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Поддерживаются PNG, JPEG, WebP, GIF, SVG",
        )
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Файл больше 8 МБ",
        )
    name = f"{secrets.token_hex(12)}{ext}"
    (UPLOAD_DIR / name).write_bytes(data)
    # относительный URL — надёжно за прокси (браузер резолвит от origin)
    return MediaUploadOut(url=f"/api/uploads/{name}")
