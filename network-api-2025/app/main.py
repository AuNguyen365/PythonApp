from fastapi import FastAPI
from app.auth import router as auth_router
from app.blog import router as blog_router
from app.config import settings


app = FastAPI(title=settings.APP_NAME)
app.include_router(auth_router) # Public
app.include_router(blog_router) # Public + Private (Bearer)


@app.get("/")
def root():
    return {"message": f"Welcome to {settings.APP_NAME}"}