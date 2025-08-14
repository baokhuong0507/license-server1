# app/services/keys.py

from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from .. import models

def check_and_update_all_keys_status(db: Session):
    """
    Hàm này sẽ kiểm tra và cập nhật trạng thái của tất cả các key.
    Nó sẽ chạy mỗi khi trang quản lý được tải.
    --> Đây là giải pháp cho vấn đề #1.
    """
    now = datetime.now(timezone.utc)
    
    # Lấy TẤT CẢ các key chưa bị đánh dấu là 'expired'
    keys_to_check = db.query(models.Key).filter(models.Key.status != 'expired').all()
    
    # Biến này để kiểm tra xem có thay đổi nào trong DB không
    needs_commit = False
    for key in keys_to_check:
        # Nếu key có ngày hết hạn và ngày đó đã qua, đặt trạng thái là 'expired'
        if key.expiry_date and key.expiry_date < now:
            key.status = 'expired'
            needs_commit = True
            
    # Chỉ ghi vào database nếu có sự thay đổi
    if needs_commit:
        db.commit()


def get_all_keys(db: Session) -> list[models.Key]:
    """
    Hàm để lấy danh sách key hiển thị trên trang quản trị.
    Hàm này sẽ luôn gọi hàm kiểm tra trạng thái trước.
    """
    # Bước 1: Luôn chạy kiểm tra và cập nhật trạng thái trước khi lấy dữ liệu
    check_and_update_all_keys_status(db)
    
    # Bước 2: Lấy và trả về danh sách key mới nhất từ DB
    return db.query(models.Key).order_by(models.Key.id.desc()).all()


def activate_key_by_id(db: Session, key_id: int) -> models.Key | None:
    """
    Hàm xử lý logic kích hoạt một key.
    """
    key = db.query(models.Key).filter(models.Key.id == key_id).first()
    
    # Chỉ kích hoạt khi key tồn tại và đang ở trạng thái 'unused'
    if key and key.status == 'unused':
        key.status = 'active'
        # Nếu key chưa có ngày hết hạn, mặc định là 30 ngày kể từ ngày kích hoạt
        if not key.expiry_date:
            key.expiry_date = datetime.now(timezone.utc) + timedelta(days=30)
        
        db.commit()
        db.refresh(key) # Lấy lại dữ liệu mới nhất của key từ DB
        return key
        
    # Trả về None nếu không tìm thấy key hoặc key không hợp lệ
    return None

def create_new_key(db: Session, days_valid: int | None = None) -> models.Key:
    """
    Hàm tạo một key mới, tách biệt logic khỏi router.
    """
    import random
    import string

    # Hàm tạo key ngẫu nhiên
    def generate_key_string():
        chars = string.ascii_uppercase + string.digits
        return '-'.join(''.join(random.choice(chars) for _ in range(5)) for _ in range(5))

    new_key_data = models.Key(
        key=generate_key_string(),
        status='unused'
    )

    if days_valid:
        new_key_data.expiry_date = datetime.now(timezone.utc) + timedelta(days=days_valid)

    db.add(new_key_data)
    db.commit()
    db.refresh(new_key_data)
    return new_key_data