from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers import admin_api, admin_web, client_api
from app.database import engine
from app import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Mount static + templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(admin_api.router, prefix="/api/admin", tags=["admin_api"])
app.include_router(admin_web.router, tags=["admin_web"])
app.include_router(client_api.router, prefix="/api/client", tags=["client_api"])
