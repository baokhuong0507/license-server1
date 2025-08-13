# app/services/keys.py

from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from .. import models

def check_and_update_expired_keys(db: Session):
    """
    Kiểm tra và cập nhật trạng thái cho TẤT CẢ các key đã hết hạn.
    Đây là giải pháp cho vấn đề #1.
    """
    now = datetime.now(timezone.utc)
    
    # Lấy tất cả các key chưa bị đánh dấu là 'expired' (bao gồm cả 'unused' và 'active')
    keys_to_check = db.query(models.Key).filter(models.Key.status != 'expired').all()
    
    has_changes = False
    for key in keys_to_check:
        if key.expiry_date and key.expiry_date < now:
            key.status = 'expired'
            has_changes = True
            
    if has_changes:
        db.commit()

def get_all_keys_with_status_check(db: Session) -> list[models.Key]:
    """
    Hàm chính để lấy danh sách key cho trang quản trị.
    Luôn chạy kiểm tra hết hạn trước khi trả về dữ liệu.
    """
    # Bước 1: Luôn kiểm tra và cập nhật trạng thái trước.
    check_and_update_expired_keys(db)
    
    # Bước 2: Lấy và trả về danh sách key mới nhất.
    all_keys = db.query(models.Key).order_by(models.Key.id.desc()).all()
    return all_keys

def activate_key_by_id(db: Session, key_id: int) -> models.Key | None:
    """
    Logic để kích hoạt một key cụ thể.
    Được gọi bởi router để giải quyết vấn đề #2.
    """
    key_to_activate = db.query(models.Key).filter(models.Key.id == key_id).first()
    
    # Chỉ kích hoạt nếu key tồn tại và đang ở trạng thái 'unused'
    if key_to_activate and key_to_activate.status == 'unused':
        key_to_activate.status = 'active'
        # Nếu key chưa có ngày hết hạn, đặt là 30 ngày kể từ bây giờ
        if not key_to_activate.expiry_date:
            key_to_activate.expiry_date = datetime.now(timezone.utc) + timedelta(days=30)
        
        db.commit()
        db.refresh(key_to_activate)
        return key_to_activate
        
    return None # Trả về None nếu không thể kích hoạt```

---

### **2. Tệp `app/routers/admin_web.py`**

Tệp này xử lý các yêu cầu từ trình duyệt. Tôi đã sửa lại route kích hoạt key để nó trả về một đoạn HTML (HTMX response) thay vì tải lại cả trang.

**Nội dung đầy đủ:**

```python
# app/routers/admin_web.py

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..database import get_db
from ..services import keys as keys_service

# Khởi tạo router và templates
router = APIRouter(
    prefix="/admin",
    tags=["Admin Web"]
)
templates = Jinja2Templates(directory="app/templates")


@router.get("/keys", response_class=HTMLResponse)
async def get_keys_management_page(request: Request, db: Session = Depends(get_db)):
    """
    Hiển thị trang quản lý key.
    Hàm này gọi service để lấy danh sách key (đã được kiểm tra hết hạn).
    """
    # Sử dụng hàm đã sửa ở service để đảm bảo trạng thái luôn đúng
    all_keys = keys_service.get_all_keys_with_status_check(db)
    return templates.TemplateResponse("keys.html", {"request": request, "keys": all_keys})


@router.post("/keys/{key_id}/activate", response_class=HTMLResponse)
async def htmx_handle_activate_key(request: Request, key_id: int, db: Session = Depends(get_db)):
    """
    Endpoint mà HTMX gọi để kích hoạt key và cập nhật giao diện.
    Đây là giải pháp cho vấn đề #2.
    """
    # Bước 1: Gọi service để thực hiện logic kích hoạt
    updated_key = keys_service.activate_key_by_id(db, key_id=key_id)

    # Bước 2: Render và trả về HTML của chỉ một hàng trong bảng
    # HTMX sẽ dùng đoạn HTML này để thay thế hàng cũ trên giao diện.
    return templates.TemplateResponse(
        "partials/keys_table_rows.html", 
        {
            "request": request, 
            "key": updated_key
        }
    )

# Các route khác trong admin_web.py của bạn có thể giữ nguyên...