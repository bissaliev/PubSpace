import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DatabaseError

from src.api import router as api_v1
from src.middleware import ExceptionMiddleware

FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)s:%(lineno)s %(levelname)s - "
    "%(message)s"
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    format=FORMAT,
)

app = FastAPI()
app.include_router(api_v1)
app.add_middleware(ExceptionMiddleware)


@app.exception_handler(DatabaseError)
def handler_db_error(request: Request, exc: DatabaseError) -> JSONResponse:
    logging.error("Unhandled database error", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": (
                "An unexpected error has occurred. "
                "Our admins are already working on it."
            )
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", reload=True)
