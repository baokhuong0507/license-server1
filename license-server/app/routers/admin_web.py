# app/routers/admin_web.py

from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated
from sqlalchemy.orm import Session

from app.services import keys as key_service
from app.auth import create_access_token, get_current_user
from app.config import settings
from app.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# --- Web Endpoints ---
@router.get("/admin/login", response_class=HTMLResponse, tags=["Admin Web Interface"])
async def login_page(request: Request):
    """Hiển thị trang đăng nhập."""
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/admin/login", response_class=HTMLResponse, tags=["Admin Web Interface"])
async def handle_login(request: Request, password: str = Form(...)):
    """Xử lý form đăng nhập."""
    if password != settings.ADMIN_SECRET_KEY:
        error_msg = "Mật khẩu không chính xác."
        return templates.TemplateResponse("login.html", {"request": request, "error": error_msg}, status_code=401)
    
    # Tạo token và đặt cookie
    access_token = create_access_token(data={"sub": "admin"})
    response = RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

@router.get("/admin/logout", response_class=HTMLResponse, tags=["Admin Web Interface"])
async def handle_logout():
    """Xử lý đăng xuất."""
    response = RedirectResponse(url="/admin/login")
    response.delete_cookie("access_token")
    return response

@router.get("/admin/dashboard", response_class=HTMLResponse, tags=["Admin Web Interface"])
async def dashboard(request: Request, user_logged_in: bool = Depends(get_current_user), db: Session = Depends(get_db)):
    """Hiển thị trang quản lý chính."""
    if not user_logged_in:
        return RedirectResponse(url="/admin/login")
    
    # Lấy danh sách keys từ CSDL
    all_keys = key_service.get_all_keys(db)
    
    # Thêm cờ is_logged_in vào request để template có thể dùng
    request.state.is_logged_in = True 
    
    return templates.TemplateResponse("keys.html", {"request": request, "keys": all_keys})

@router.post("/admin/add-key", response_class=RedirectResponse, tags=["Admin Web Interface"])
async def handle_add_key(key_value: str = Form(...), user_logged_in: bool = Depends(get_current_user), db: Session = Depends(get_db)):
    """Xử lý việc thêm key mới."""
    if not user_logged_in:
        return RedirectResponse(url="/admin/login")
    
    if key_value:
        key_service.create_key(db, key_value)
    
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)

@router.post("/admin/delete-key", response_class=RedirectResponse, tags=["Admin Web Interface"])
async def handle_delete_key(key_value: str = Form(...), user_logged_in: bool = Depends(get_current_user), db: Session = Depends(get_db)):
    """Xử lý việc xóa key."""
    if not user_logged_in:
        return RedirectResponse(url="/admin/login")
    
    if key_value:
        key_service.delete_key(db, key_value)

    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)

@router.post("/admin/lock-key", response_class=RedirectResponse, tags=["Admin Web Interface"])
async def handle_lock_key(key_value: str = Form(...), user_logged_in: bool = Depends(get_current_user), db: Session = Depends(get_db)):
    """Xử lý việc khóa key."""
    if not user_logged_in:
        return RedirectResponse(url="/admin/login")
    
    key_service.update_key_status(db, key_value, "revoked")
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)

@router.post("/admin/unlock-key", response_class=RedirectResponse, tags=["Admin Web Interface"])
async def handle_unlock_key(key_value: str = Form(...), user_logged_in: bool = Depends(get_current_user), db: Session = Depends(get_db)):
    """Xử lý việc mở khóa key (trở về trạng thái active)."""
    if not user_logged_in:
        return RedirectResponse(url="/admin/login")
    
    key_service.update_key_status(db, key_value, "active")
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)
