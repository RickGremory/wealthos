from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from wealthos.core.logging import configure_logging, get_logger


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    log = get_logger("wealthos.lifespan")
    log.info("starting_api")
    yield
    log.info("stopping_api")
