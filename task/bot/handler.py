import re
from typing import Any, Dict, Union

from discord import Message
from loguru import logger

from lib.handler import PROMPT_PREFIX, PROMPT_SUFFIX
from lib.api import RESULT_TABLE
from task.bot._typing import Attachment, CallbackData, Embed
from util._queue import taskqueue

TRIGGER_ID_PATTERN = f"{PROMPT_PREFIX}(\w+?){PROMPT_SUFFIX}"  # 消息 ID 正则

TEMP_MAP: Dict[str, bool] = {}  # 临时存储消息流转信息


def get_temp(trigger_id: str):
  return TEMP_MAP.get(trigger_id)


def set_temp(trigger_id: str):
  TEMP_MAP[trigger_id] = True


def pop_temp(trigger_id: str):
  taskqueue.pop(trigger_id)
  TEMP_MAP.pop(trigger_id, None)
  logger.debug(f"queue_release: {trigger_id}")


def match_trigger_id(content: str) -> Union[str, None]:
  match = re.findall(TRIGGER_ID_PATTERN, content)
  return match[0] if match else None


async def callback_trigger(trigger_id: str, trigger_status: str,
                           message: Message):
  data = CallbackData(
      type=trigger_status,
      id=message.id,
      content=message.content,
      attachments=[
          Attachment(**attachment.to_dict())
          for attachment in message.attachments
      ],
      embeds=[],
      trigger_id=trigger_id,
  )
  RESULT_TABLE[trigger_id] = data
  logger.debug(f"callback data: {data}")


async def callback_describe(trigger_status: str, message: Message,
                            embed: Dict[str, Any]):
  url = embed.get("image", {}).get("url")
  trigger_id = url.split("/")[-1].split(".")[0]

  RESULT_TABLE[trigger_id] = CallbackData(
      type=trigger_status,
      id=message.id,
      content=message.content,
      attachments=[],
      embeds=[Embed(**embed)],
      trigger_id=trigger_id,
  )
  return trigger_id
