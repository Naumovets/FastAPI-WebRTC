from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from pages.router import router as router_pages
from calls.router import router as router_calls

app = FastAPI()

app.include_router(router_pages)
app.include_router(router_calls)

app.mount("/static", StaticFiles(directory="static"), name="static")


