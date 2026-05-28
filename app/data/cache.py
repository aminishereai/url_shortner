from typing import Annotated
from fastapi import Depends, HTTPException, Request, status, FastAPI
from pydantic import HttpUrl

import redis.asyncio as redis
from redis.exceptions import ConnectionError

from contextlib import asynccontextmanager

from app.services.logger import logger
from app.config import REDIS_HOST, REDIS_PORT, REDIS_MAX_CONNECTIONS


@asynccontextmanager
async def lifespan(app : FastAPI):
    """Manage Redis connection lifecycle."""
    try:
        app.state.redis = redis.from_url(
            f"redis://{REDIS_HOST}:{REDIS_PORT}",
            encoding="utf-8",
            decode_responses=True,
            max_connections=REDIS_MAX_CONNECTIONS
        )
        connected = await app.state.redis.ping()  # type: ignore
        if connected:
            logger.info(f"Redis connected to {REDIS_HOST}:{REDIS_PORT}")
    except ConnectionError as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise RuntimeError("Redis is not Connected")
    
    yield
    await app.state.redis.aclose()
    logger.info("Redis connection closed")

async def get_redis_v1():
    """Return an async Redis client (do not await from_url)."""
    return redis.from_url(
        f"redis://{REDIS_HOST}:{REDIS_PORT}",
        decode_responses=True
    )

async def get_redis_v2(request : Request):
    return request.app.state.redis

RedisDep = Annotated[redis.Redis, Depends(get_redis_v2)]


async def set_key_value(r: redis.Redis, key: str, url: HttpUrl, request : Request ,ex: int | None = None  ) -> bool:
    if not isinstance(key, str):
        logger.error("Given Key is not string" , extra={"request_id" : request.state.request_id})
        raise ValueError("Key must be a string")
    
    try:
        result = await r.set(key, str(url), ex=ex, nx=True)
        if result:
            logger.info(f"Key set Successfully {key}")
            return True
        else:
            logger.info(f"Key is already present {key}")
            return False
    except Exception as e:
        print(f"Unknown error occurred : {e}")
        logger.error(f"Unknown error occurred : {e}" , extra={"Exception" : e})
        raise

async def get_value(r: redis.Redis, key: str, request : Request ) -> str: 
    value = await r.get(key)
    if not value:
        logger.error("Key not found" , extra={"request_id" : request.state.request_id ,"exception" : "404 not found"})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Key not found",
        )
    return str(value)


async def delete(r: redis.Redis, key: str, request : Request):
    try :
        return await r.delete(key)
    except Exception as e:
        logger.error(f"Failed to delete the key-value" , extra={"request_id" : request.state.request_id ,"exception" : e})

if __name__ == "__main__":
    pass