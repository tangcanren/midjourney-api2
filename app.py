from contextlib import asynccontextmanager
from os import getenv

from anyio import create_task_group, to_thread
from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import lib.routers as routers
from lib.exceptions import APPBaseException, ErrorCode, MissRequiredVariableError
from task.bot.listener import bot
#tes
BOT_TOKEN = getenv("BOT_TOKEN")
if not BOT_TOKEN:
  raise MissRequiredVariableError(
      "Missing required environment variable: [BOT_TOKEN]")


@asynccontextmanager
async def lifespan(app: FastAPI):
  async with create_task_group() as tg:
    tg.start_soon(to_thread.run_sync, bot.run, BOT_TOKEN)
    yield


app = FastAPI(title="Midjourney API", lifespan=lifespan)


@app.exception_handler(RequestValidationError)
def validation_exception_handler(_, exc: RequestValidationError):
  return JSONResponse(
      status_code=status.HTTP_400_BAD_REQUEST,
      content={
          "code": ErrorCode.REQUEST_PARAMS_ERROR.value,
          "message": f"request params error: {exc.body}"
      },
  )


@app.exception_handler(APPBaseException)
def validation_exception_handler(_, exc: APPBaseException):
  return JSONResponse(
      status_code=status.HTTP_200_OK,
      content={
          "code": exc.code.value,
          "message": exc.message
      },
  )


app.include_router(routers.router, prefix="/v1/api/trigger")
