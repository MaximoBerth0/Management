from fastapi import FastAPI

from app.config import settings
from app.users.routers import router as users_router

app = FastAPI(title=settings.APP_NAME)


@app.get("/")
async def root():
    return {"message": "Management is running"}


app.include_router(users_router)
