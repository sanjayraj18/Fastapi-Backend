from fastapi import FastAPI, status, HTTPException
from routes.post_routes import router as post_router

app = FastAPI()
app.include_router(post_router)