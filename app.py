import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.responses import JSONResponse

from hotrank.infrastructure import lifespan, limiter
from hotrank.routers.general import router as general_router
from hotrank.routers.rankings import router as rankings_router
from hotrank.routers.agent import router as agent_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def rate_limit_exceeded_handler(
    request: Request,
    _exc: RateLimitExceeded,
) -> JSONResponse:
    current_limit, limit_args = request.state.view_rate_limit
    reset_at, remaining = limiter.limiter.get_window_stats(
        current_limit,
        *limit_args,
    )
    retry_after = max(int(reset_at - time.time()) + 1, 1)
    return JSONResponse(
        status_code=429,
        headers={
            "Retry-After": str(retry_after),
            "X-RateLimit-Limit": str(current_limit.amount),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_at),
        },
        content={
            "code": 429,
            "msg": "请求过于频繁，请稍后再试。",
            "data": {
                "error": {
                    "code": "RATE_LIMITED",
                    "message": "请求过于频繁，请稍后再试。",
                    "retryable": True,
                    "retry_after_seconds": retry_after,
                }
            },
        },
    )


app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

app.include_router(general_router)
app.include_router(rankings_router)
app.include_router(agent_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
