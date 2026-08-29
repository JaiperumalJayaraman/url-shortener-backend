import secrets
import string
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import URL

ALPHABET = string.ascii_letters + string.digits

def generate_code(length: int = 7) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))

def create_short_url(db: Session, original_url: str, alias: str | None, expires_at):
    if alias and db.scalar(select(URL).where(URL.short_code == alias)):
        raise ValueError("Custom alias already exists")

    code = alias or generate_code()
    while db.scalar(select(URL).where(URL.short_code == code)):
        code = generate_code()

    item = URL(short_code=code, original_url=str(original_url), expires_at=expires_at)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def get_active_url(db: Session, code: str):
    item = db.scalar(select(URL).where(URL.short_code == code))
    if not item:
        return None
    if item.expires_at and item.expires_at <= datetime.now(timezone.utc).replace(tzinfo=None):
        return None
    return item
