from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import bcrypt

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

templates = Jinja2Templates(directory="app/templates")

ADMIN_USER = "admin"
ADMIN_PASS_HASH = bcrypt.hashpw("123456".encode(), bcrypt.gensalt())

# Login page
@app.get("/admin/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/admin/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USER and bcrypt.checkpw(password.encode(), ADMIN_PASS_HASH):
        request.session["admin"] = True
        return RedirectResponse(url="/admin/monitor", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Sai tài khoản hoặc mật khẩu"})

@app.get("/admin/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/admin/login", status_code=302)

def require_admin(request: Request):
    if not request.session.get("admin"):
        raise HTTPException(status_code=403, detail="Not authorized")

# Monitor keys
@app.get("/admin/monitor", response_class=HTMLResponse)
async def monitor(request: Request):
    require_admin(request)
    keys = []  # TODO: Lấy danh sách key và trạng thái từ DB
    return templates.TemplateResponse("monitor.html", {"request": request, "keys": keys})

@app.post("/admin/force-unbind")
async def force_unbind(request: Request, key_id: str = Form(...)):
    require_admin(request)
    # TODO: Cập nhật DB để unbind key này
    return RedirectResponse(url="/admin/monitor", status_code=302)
