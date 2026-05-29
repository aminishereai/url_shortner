from http import HTTPStatus

from fastapi import FastAPI, HTTPException, Request , status
from starlette.exceptions import HTTPException as StarletteHTTPExceptions
from fastapi.responses import JSONResponse, RedirectResponse

from app.data.cache import lifespan
from app.routers import access


from uuid import uuid4

from app.schemas import ProblemDetail

app = FastAPI(lifespan=lifespan)


@app.exception_handler(StarletteHTTPExceptions)
async def http_exception_handler(request : Request , exc : HTTPException):
    status_code = exc.status_code
    problem = ProblemDetail(
        title=HTTPStatus(status_code).phrase,
        status=status_code,
        detail=exc.detail,
        instance=request.url.path
    )

    return JSONResponse(
        status_code=status_code,
        content=problem.model_dump()
    )

@app.middleware("http")
async def request_id_middleware(request : Request , call_next):
    id = uuid4()
    request.state.request_id = id
    response = await call_next(request)
    return response  



@app.get("/")
async def main():
    return RedirectResponse(url="/urls" , status_code=status.HTTP_308_PERMANENT_REDIRECT)



app.include_router(access.router)
