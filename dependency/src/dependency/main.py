from fastapi import FastAPI
from routes.post_routes import router as post_router
from routes.user_routes import router as user_router
import logging
from core.logging_config import setup_logging
from middleware.request_id import RequestIDMiddleware
from middleware.logging import LoggingMiddleware
from middleware.exception_handlers import register_exception_handlers


setup_logging("DEBUG")
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)

register_exception_handlers(app)

app.include_router(post_router)
app.include_router(user_router)
 
@app.get("/health")
def health():
    return {"status": "ok"}