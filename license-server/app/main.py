from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers import admin_api, admin_web, client_api

# Nếu bạn dùng render hoặc server như Uvicorn
import os

app = FastAPI(title="License Server")

# Mount API routers
app.include_router(admin_api.router, prefix="/api/admin")
app.include_router(admin_web.router, prefix="/admin")
app.include_router(client_api.router, prefix="/api")

# Static & template
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Root route
@app.get("/")
async def root():
    return {"message": "License Server is running"}
