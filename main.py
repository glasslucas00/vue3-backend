#!/usr/bin/python3

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from core import metro,abnorm,train
from database.configuration import engine
from models import models
from decouple import config
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DogeAPI",
    description="API with high performance built with FastAPI & SQLAlchemy, help to improve connection with your Backend Side.",
    version="1.0.0",
)
origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(metro.router)
app.include_router(abnorm.router)
app.include_router(train.router)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """      
    Home page

    Args:
        request (Request): Request object

    Returns:
        HTMLResponse: HTML response
    """
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == '__main__':
    # uvicorn.run(app, host="127.0.0.1", port=8800, reload=True, debug=True)
    uvicorn.run(app='main:app', host=config("HOST"), port=config("PORT",cast=int), reload=True, debug=True)
    # uvicorn.run(app, host=config("HOST"), port=config("PORT",cast=int))