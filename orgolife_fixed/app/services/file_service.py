import logging
import uuid
import os
import aiofiles
from fastapi import UploadFile, HTTPException, status
from app.db.database import get_database
from app.core.config import settings

logger = logging.getLogger(__name__)

ALLOWED_MIME_MAP = {
    b"%PDF": "application/pdf",
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG": "image/png",
}

MIME_TO_EXT = {
    "application/pdf": "pdf",
    "image/jpeg": "jpg",
    "image/png": "png",
}


def _sniff_mime(header: bytes) -> str:
    """Detect MIME type from the first 4 bytes (magic bytes)."""
    for magic, mime in ALLOWED_MIME_MAP.items():
        if header.startswith(magic):
            return mime
    return "unknown"


async def save_upload(
    file: UploadFile,
    bucket: str,
    user_id: str,
    field_name: str,
) -> str:
    """
    Validate and upload file to Supabase Storage.
    Returns the cloud path (e.g. 'user_id/filename.pdf').
    """
    content = await file.read()
    size = len(content)

    if size == 0:
        raise HTTPException(status_code=400, detail="File is empty")
    if size > settings.max_file_size_bytes:
        raise HTTPException(status_code=413, detail="File too large")

    mime = _sniff_mime(content[:4])
    if mime == "unknown":
        raise HTTPException(status_code=415, detail="Unsupported file type")

    ext = MIME_TO_EXT[mime]
    uid = uuid.uuid4().hex[:6]
    filename = f"{field_name}_{uid}.{ext}"
    cloud_path = f"{user_id}/{filename}"

    try:
        supabase = get_database()
        # Try Cloud Upload First
        res = supabase.storage.from_(bucket).upload(
            path=cloud_path,
            file=content,
            file_options={"content-type": mime}
        )
        logger.info(f"Cloud Upload Success [{bucket}]: {cloud_path}")
        return cloud_path
    except Exception as e:
        logger.warning(f"Cloud storage failed (Bucket '{bucket}' likely missing). Falling back to local disk. Error: {e}")
        
        # LOCAL FALLBACK
        dir_path = os.path.join(settings.UPLOAD_DIR, bucket)
        os.makedirs(dir_path, exist_ok=True)
        local_filename = f"{user_id}_{field_name}_{uid}.{ext}"
        local_path = os.path.join(dir_path, local_filename)
        
        async with aiofiles.open(local_path, "wb") as out:
            await out.write(content)
        
        logger.info(f"Local Fallback Success: {local_path}")
        return local_path


def get_signed_url(bucket: str, path: str, expires_in: int = 3600) -> str:
    """Generate signed URL with fallback for local files."""
    if not path: return ""
    
    # Check if this is a local path (contains directory separators or doesn't follow cloud pattern)
    if "uploads" in path or os.path.isabs(path) or "\\" in path or "/" in path and not path.split("/")[0].isalnum():
        return "/" + path.replace("\\", "/")

    try:
        supabase = get_database()
        res = supabase.storage.from_(bucket).create_signed_url(path, expires_in)
        return res.get("signedURL") or ""
    except Exception as e:
        # Final fallback: return the original path as a local URL
        return "/" + path.replace("\\", "/")


def file_url(path: str) -> str:
    """Legacy helper — now returns path if URL signature not needed at this layer."""
    return path
