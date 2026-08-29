from collections import defaultdict
from datetime import datetime, timezone
from time import monotonic
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from .config import settings
from .database import Base, engine, get_db
from .models import URL
from .schemas import HealthResponse, URLCreate, URLResponse
from .services import create_short_url, get_active_url

Base.metadata.create_all(bind=engine)
app = FastAPI(title="URL Shortener API", version="1.0.0", description="Scalable URL shortening backend")

_hits = defaultdict(list)

def check_rate_limit(request: Request):
    now = monotonic()
    key = request.client.host if request.client else "unknown"
    window_start = now - 60
    _hits[key] = [t for t in _hits[key] if t > window_start]
    if len(_hits[key]) >= settings.rate_limit_per_minute:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    _hits[key].append(now)

def response_for(item: URL):
    return URLResponse(
        short_code=item.short_code,
        short_url=f"{settings.base_url.rstrip('/')}/{item.short_code}",
        original_url=item.original_url,
        created_at=item.created_at,
        expires_at=item.expires_at,
        click_count=item.click_count,
    )

@app.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok"}

@app.post("/api/v1/urls", response_model=URLResponse, status_code=201)
def shorten(payload: URLCreate, request: Request, db: Session = Depends(get_db)):
    check_rate_limit(request)
    if payload.expires_at and payload.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Expiration must be in the future")
    try:
        item = create_short_url(db, str(payload.original_url), payload.custom_alias, payload.expires_at)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return response_for(item)

@app.get("/{short_code}", include_in_schema=False)
def redirect(short_code: str, db: Session = Depends(get_db)):
    item = get_active_url(db, short_code)
    if not item:
        raise HTTPException(status_code=404, detail="Short URL not found or expired")
    item.click_count += 1
    db.commit()
    return RedirectResponse(item.original_url, status_code=307)

@app.get("/api/v1/urls/{short_code}", response_model=URLResponse)
def details(short_code: str, db: Session = Depends(get_db)):
    item = get_active_url(db, short_code)
    if not item:
        raise HTTPException(status_code=404, detail="Short URL not found or expired")
    return response_for(item)

@app.delete("/api/v1/urls/{short_code}", status_code=204)
def delete(short_code: str, request: Request, db: Session = Depends(get_db)):
    check_rate_limit(request)
    item = db.query(URL).filter(URL.short_code == short_code).first()
    if not item:
        raise HTTPException(status_code=404, detail="Short URL not found")
    db.delete(item)
    db.commit()
    return None

@app.get("/api/v1/stats")
def stats(db: Session = Depends(get_db)):
    urls = db.query(URL).all()
    return {
        "total_urls": len(urls),
        "total_clicks": sum(item.click_count for item in urls),
        "active_urls": sum(
            1 for item in urls
            if not item.expires_at or item.expires_at > datetime.now(timezone.utc).replace(tzinfo=None)
        ),
    }
