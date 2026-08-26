from fastapi import FastAPI, status, HTTPException
from routes.post_routes import router as post_router
from routes.user_routes import router as user_router
import logging
from core.logging_config import setup_logging
from middleware.request_id import RequestIDMiddleware


setup_logging("DEBUG")
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(RequestIDMiddleware)

app.include_router(post_router)
app.include_router(user_router)
 
@app.get("/health")
def health():
    logger.info("health_check")
    return {"status": "ok"}