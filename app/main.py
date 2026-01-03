from fastapi import FastAPI

from app.auth.routers import router as auth_router
from app.config import settings
from app.users.routers import router as users_router

app = FastAPI(title=settings.APP_NAME)


@app.get("/")
def root():
    return {"message": "Management is running"}


app.include_router(users_router)
app.include_router(auth_router)