from fastapi import Request
from ..utils.logger import get_logger

logger = get_logger(__name__)

async def log_request(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Completed {request.method} {request.url} - {response.status_code}")
    return response