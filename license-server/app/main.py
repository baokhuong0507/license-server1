from fastapi import FastAPI, Request, Depends, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from pathlib import Path
from datetime import datetime, timedelta
import io, csv, bcrypt
from typing import Optional
from .models import (
    Base, User, LicenseKey, KeyStatus,
    Activation, ActivationStatus
)
from .deps import engine, get_db
from .routers.client_api import router as client_api_router
from .services.keys import set_key_status
from .config import settings

app = FastAPI(title="License Server")
app.add_middleware(SessionMiddleware, secret_key=settings.JWT_SECRET)

static_dir = Path("app/static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

templates = Jinja2Templates(directory="app/templates")

# Tạo bảng & admin mặc định
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

# ========= ĐĂNG NHẬP / ĐĂNG XUẤT =========
@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_form(request: Request):
    if request.session.get("admin_email"):
        return RedirectResponse(url="/admin/keys", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/admin/login")
async def admin_login(
    request: Request,
    email: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    # nếu form trống -> trả lại trang login với thông báo
    if not email or not password:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Vui lòng nhập email và mật khẩu"},
            status_code=400,
        )

    user = db.query(User).filter_by(email=email).first()
    if not user or not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Sai email hoặc mật khẩu"},
            status_code=401,
        )

    request.session["admin_email"] = user.email
    return RedirectResponse(url="/admin/keys", status_code=303)

@app.get("/admin/logout")
async def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/admin/login", status_code=303)

# ========= QUẢN LÝ KEY =========
@app.get("/admin/keys", response_class=HTMLResponse)
async def admin_keys(
    request: Request,
    q: str = Query("", description="tìm theo key hoặc ghi chú"),
    status: str = Query("ALL"),
    db: Session = Depends(get_db),
):
    if not request.session.get("admin_email"):
        return RedirectResponse(url="/admin/login", status_code=303)

    query = db.query(LicenseKey)
    if q:
        like = f"%{q}%"
        query = query.filter((LicenseKey.key.ilike(like)) | (LicenseKey.note.ilike(like)))
    if status and status != "ALL":
        try:
            s = KeyStatus[status]
            query = query.filter(LicenseKey.status == s)
        except KeyError:
            pass
    keys = query.order_by(LicenseKey.created_at.desc()).all()
    return templates.TemplateResponse("keys.html", {"request": request, "keys": keys, "KeyStatus": KeyStatus, "q": q, "status": status})

@app.post("/admin/keys")
async def create_key(request: Request, key: str = Form(...), note: str = Form(""), db: Session = Depends(get_db)):
    if not request.session.get("admin_email"):
        return RedirectResponse(url="/admin/login", status_code=303)
    if not key:
        return RedirectResponse(url="/admin/keys", status_code=303)
    k = LicenseKey(key=key.strip(), note=note.strip() or None)
    db.add(k); db.commit()
    return RedirectResponse(url="/admin/keys", status_code=303)

@app.post("/admin/keys/{key_id}/update")
async def key_update(key_id: str, note: str = Form(""), db: Session = Depends(get_db), request: Request = None):
    if not request.session.get("admin_email"):
        return RedirectResponse(url="/admin/login", status_code=303)
    k = db.query(LicenseKey).get(key_id)
    if k:
        k.note = (note or "").strip() or None
        db.commit()
    return RedirectResponse(url="/admin/keys", status_code=303)

@app.post("/admin/keys/{key_id}/enable")
async def key_enable(key_id: str, request: Request, db: Session = Depends(get_db)):
    if not request.session.get("admin_email"):
        return RedirectResponse(url="/admin/login", status_code=303)
    k = db.query(LicenseKey).get(key_id)
    set_key_status(db, k, KeyStatus.ACTIVE)
    return RedirectResponse(url="/admin/keys", status_code=303)

@app.post("/admin/keys/{key_id}/disable")
async def key_disable(key_id: str, request: Request, db: Session = Depends(get_db)):
    if not request.session.get("admin_email"):
        return RedirectResponse(url="/admin/login", status_code=303)
    k = db.query(LicenseKey).get(key_id)
    set_key_status(db, k, KeyStatus.DISABLED)
    return RedirectResponse(url="/admin/keys", status_code=303)

@app.post("/admin/keys/{key_id}/lock")
async def key_lock(key_id: str, request: Request, db: Session = Depends(get_db)):
    if not request.session.get("admin_email"):
        return RedirectResponse(url="/admin/login", status_code=303)
    k = db.query(LicenseKey).get(key_id)
    set_key_status(db, k, KeyStatus.TEMP_LOCKED)
    return RedirectResponse(url="/admin/keys", status_code=303)

@app.post("/admin/keys/{key_id}/unlock")
async def key_unlock(key_id: str, request: Request, db: Session = Depends(get_db)):
    if not request.session.get("admin_email"):
        return RedirectResponse(url="/admin/login", status_code=303)
    k = db.query(LicenseKey).get(key_id)
    set_key_status(db, k, KeyStatus.ACTIVE)
    return RedirectResponse(url="/admin/keys", status_code=303)

@app.post("/admin/keys/{key_id}/delete")
async def key_delete(key_id: str, request: Request, db: Session = Depends(get_db)):
    if not request.session.get("admin_email"):
        return RedirectResponse(url="/admin/login", status_code=303)
    k = db.query(LicenseKey).get(key_id)
    set_key_status(db, k, KeyStatus.DELETED)
    return RedirectResponse(url="/admin/keys", status_code=303)

@app.get("/admin/keys/export")
async def keys_export(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("admin_email"):
        return RedirectResponse(url="/admin/login", status_code=303)
    rows = db.query(LicenseKey).order_by(LicenseKey.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["key", "status", "note", "created_at", "updated_at"]) 
    for k in rows:
        writer.writerow([k.key, k.status.value, k.note or "", k.created_at, k.updated_at])
    output.seek(0)
    headers = {
        "Content-Disposition": "attachment; filename=keys.csv"
    }
    return StreamingResponse(iter([output.read()]), media_type="text/csv", headers=headers)

# ========= MONITOR ONLINE =========
@app.get("/admin/monitor", response_class=HTMLResponse)
async def admin_monitor(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("admin_email"):
        return RedirectResponse(url="/admin/login", status_code=303)
    cutoff = datetime.utcnow() - timedelta(seconds=120)
    acts = db.query(Activation).filter(Activation.status==ActivationStatus.BOUND).all()
    rows = []
    for a in acts:
        if a.last_seen_at and a.last_seen_at >= cutoff:
            rows.append({
                "activation_id": a.id,
                "key": a.license_key.key,
                "fingerprint": a.device.fingerprint,
                "last_seen": a.last_seen_at,
            })
    return templates.TemplateResponse("monitor.html", {"request": request, "rows": rows})

@app.post("/admin/force-unbind/{activation_id}")
async def admin_force_unbind(activation_id: str, request: Request, db: Session = Depends(get_db)):
    if not request.session.get("admin_email"):
        return RedirectResponse(url="/admin/login", status_code=303)
    a = db.get(Activation, activation_id)
    if a:
        a.status = ActivationStatus.UNBOUND
        a.unbound_at = datetime.utcnow()
        db.commit()
    return RedirectResponse(url="/admin/monitor", status_code=303)

# ========= API CLIENT =========
app.include_router(client_api_router)
