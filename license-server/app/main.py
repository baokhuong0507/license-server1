from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .models import Base, User, LicenseKey, KeyStatus
from .deps import engine, get_db
from .routers.client_api import router as client_api_router
from .services.keys import set_key_status
import bcrypt

app = FastAPI(title="License Server")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Create tables & default admin on startup
Base.metadata.create_all(bind=engine)

def ensure_admin(db: Session):
    admin = db.query(User).filter_by(email="admin@example.com").first()
    if not admin:
        pw_hash = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode()
        admin = User(email="admin@example.com", password_hash=pw_hash)
        db.add(admin); db.commit()

@app.on_event("startup")
async def startup_event():
    with next(get_db()) as db:
        ensure_admin(db)

# Simple admin page (no login yet)
@app.get("/admin/keys", response_class=HTMLResponse)
def admin_keys(request: Request, db: Session = Depends(get_db)):
    keys = db.query(LicenseKey).order_by(LicenseKey.created_at.desc()).all()
    return templates.TemplateResponse("keys.html", {"request": request, "keys": keys, "KeyStatus": KeyStatus})

@app.post("/admin/keys")
async def create_key(key: str = Form(...), note: str = Form(""), db: Session = Depends(get_db)):
    k = LicenseKey(key=key, note=note)
    db.add(k); db.commit()
    return RedirectResponse(url="/admin/keys", status_code=303)

@app.post("/admin/keys/{key_id}/enable")
async def key_enable(key_id: str, db: Session = Depends(get_db)):
    k = db.query(LicenseKey).get(key_id)
    set_key_status(db, k, KeyStatus.ACTIVE)
    return RedirectResponse(url="/admin/keys", status_code=303)

@app.post("/admin/keys/{key_id}/disable")
async def key_disable(key_id: str, db: Session = Depends(get_db)):
    k = db.query(LicenseKey).get(key_id)
    set_key_status(db, k, KeyStatus.DISABLED)
    return RedirectResponse(url="/admin/keys", status_code=303)

@app.post("/admin/keys/{key_id}/lock")
async def key_lock(key_id: str, db: Session = Depends(get_db)):
    k = db.query(LicenseKey).get(key_id)
    set_key_status(db, k, KeyStatus.TEMP_LOCKED)
    return RedirectResponse(url="/admin/keys", status_code=303)

@app.post("/admin/keys/{key_id}/unlock")
async def key_unlock(key_id: str, db: Session = Depends(get_db)):
    k = db.query(LicenseKey).get(key_id)
    set_key_status(db, k, KeyStatus.ACTIVE)
    return RedirectResponse(url="/admin/keys", status_code=303)

@app.post("/admin/keys/{key_id}/delete")
async def key_delete(key_id: str, db: Session = Depends(get_db)):
    k = db.query(LicenseKey).get(key_id)
    set_key_status(db, k, KeyStatus.DELETED)
    return RedirectResponse(url="/admin/keys", status_code=303)

# Mount client API
app.include_router(client_api_router)
