# app/routers/admin_web.py

from fastapi import APIRouter, Request, Depends, Form, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.services import keys as key_service
from app.auth import get_current_user, create_access_token
from app.config import settings
from app.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/admin/login", response_class=HTMLResponse, tags=["Admin Web Interface"])
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/admin/login", response_class=HTMLResponse, tags=["Admin Web Interface"])
async def handle_login(request: Request, password: str = Form(...)):
    if password != settings.ADMIN_SECRET_KEY:
        error_msg = "Mật khẩu không chính xác."
        return templates.TemplateResponse("login.html", {"request": request, "error": error_msg}, status_code=401)
    
    access_token = create_access_token(data={"sub": "admin"})
    response = RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

@router.get("/admin/logout", response_class=HTMLResponse, tags=["Admin Web Interface"])
async def handle_logout():
    response = RedirectResponse(url="/admin/login")
    response.delete_cookie("access_token")
    return response

@router.get("/admin/dashboard", response_class=HTMLResponse, tags=["Admin Web Interface"])
async def dashboard(request: Request, user_logged_in: bool = Depends(get_current_user)):
    if not user_logged_in:
        return RedirectResponse(url="/admin/login")
    
    request.state.is_logged_in = True 
    return templates.TemplateResponse("keys.html", {"request": request})