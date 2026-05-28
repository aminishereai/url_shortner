from fastapi import APIRouter, Request , status
from fastapi.responses import RedirectResponse

from app.data import cache
from app.services.logger import logger
from app.services.shortner import generate_hash

from pydantic import HttpUrl



router = APIRouter(
    prefix="/urls",
    tags=["urls Point"]
)

@router.get("/")
async def get_all(r : cache.RedisDep):
    keys = await r.keys()
    values = await r.mget(keys)
    kvpairs = dict(zip(keys , values))
    return kvpairs



@router.get("/{hash}")
async def get_url(hash : str , r : cache.RedisDep , request : Request):
    url = await cache.get_value(r , hash , request=request)
    logger.info(f"Successfully completed the redirection of hash {hash}" , extra={"request_id" : request.state.request_id})
    return RedirectResponse(url=url , status_code=status.HTTP_308_PERMANENT_REDIRECT)



@router.post("/")
async def post_url(url : HttpUrl , r : cache.RedisDep , request : Request):
    hash = generate_hash(url)
    await cache.set_key_value(r, hash, url , request=request)

    url_db = await cache.get_value(r, hash , request=request)
    fhash = request.url_for("get_url" ,hash=hash)
    return { "url" : url_db ,"hash" : fhash._url}