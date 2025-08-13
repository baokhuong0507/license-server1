# DÁN VÀO CUỐI TỆP app/routers/admin_web.py

@router.post("/admin/lock-key", response_class=RedirectResponse)
async def handle_lock_key(key_value: str = Form(...), user_logged_in: bool = Depends(get_current_user), db: Session = Depends(get_db)):
    """Xử lý việc khóa key."""
    if not user_logged_in:
        return RedirectResponse(url="/admin/login")
    
    key_service.update_key_status(db, key_value, "revoked")
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)

@router.post("/admin/unlock-key", response_class=RedirectResponse)
async def handle_unlock_key(key_value: str = Form(...), user_logged_in: bool = Depends(get_current_user), db: Session = Depends(get_db)):
    """Xử lý việc mở khóa key (trở về trạng thái active)."""
    if not user_logged_in:
        return RedirectResponse(url="/admin/login")
    
    key_service.update_key_status(db, key_value, "active")
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)
