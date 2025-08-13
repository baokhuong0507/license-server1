# app/routers/admin_web.py

from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import keys as key_service
from app.auth import create_access_token
from app.config import settings
from jose import jwt, JWTError

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# --- Dependency để kiểm tra Cookie ---
async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        # Giải mã token để chắc chắn nó hợp lệ
        jwt.decode(token, settings.ADMIN_SECRET_KEY, algorithms=["HS256"])
        return True # Đăng nhập hợp lệ
    except JWTError:
        return None

# --- Web Endpoints ---
@router.get("/admin/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Hiển thị trang đăng nhập."""
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/admin/login", response_class=HTMLResponse)
async def handle_login(request: Request, password: str = Form(...)):
    """Xử lý form đăng nhập."""
    # Trong thực tế, bạn sẽ so sánh với mật khẩu đã hash.
    # Ở đây ta so sánh trực tiếp với một biến cấu hình cho đơn giản.
    if password != settings.ADMIN_SECRET_KEY:
        error_msg = "Mật khẩu không chính xác."
        return templates.TemplateResponse("login.html", {"request": request, "error": error_msg}, status_code=401)
    
    # Tạo token và đặt cookie
    access_token = create_access_token(data={"sub": "admin"})
    response = RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

@router.get("/admin/logout", response_class=HTMLResponse)
async def handle_logout():
    """Xử lý đăng xuất."""
    response = RedirectResponse(url="/admin/login")
    response.delete_cookie("access_token")
    return response

@router.get("/admin/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user_logged_in: bool = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user_logged_in:
        return RedirectResponse(url="/admin/login")
    all_keys = key_service.get_all_keys(db)
    request.state.is_logged_in = True 
    return templates.TemplateResponse("keys.html", {"request": request, "keys": all_keys})
    
    # Lấy danh sách keys từ CSDL
    conn = key_service.get_db_connection()
    all_keys = conn.execute("SELECT * FROM keys ORDER BY created_at DESC").fetchall()
    conn.close()
    
    # Thêm cờ is_logged_in vào request để template có thể dùng
    request.state.is_logged_in = True 
    
    return templates.TemplateResponse("keys.html", {"request": request, "keys": all_keys})

@router.post("/admin/add-key", response_class=RedirectResponse)
async def handle_add_key(key_value: str = Form(...), user_logged_in: bool = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user_logged_in:
        return RedirectResponse(url="/admin/login")
    if key_value:
        key_service.create_key(db, key_value)
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)

@router.post("/admin/delete-key", response_class=RedirectResponse)
async def handle_delete_key(key_value: str = Form(...), user_logged_in: bool = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user_logged_in:
        return RedirectResponse(url="/admin/login")
    if key_value:
        key_service.delete_key(db, key_value)
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)
