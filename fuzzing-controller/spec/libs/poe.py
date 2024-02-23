import asyncio
import logging
logging.getLogger("httpx").setLevel(logging.WARNING)
from typing import AsyncIterable
from collections import Counter
import tiktoken

from fastapi_poe.types import ProtocolMessage
from fastapi_poe.client import get_bot_response
from fastapi_poe import PoeBot, run
from fastapi_poe.client import stream_request
from fastapi_poe.types import (
    MetaResponse as MetaMessage,
    PartialResponse as BotMessage,
    ProtocolMessage,
    QueryRequest,
    SettingsResponse,
)
from libs.constants import API_KEY, LLM_MODEL

class BotError(Exception):
    """Raised when there is an error communicating with the bot."""

def select_most_frequent_answer(answers):
    frequency_summary = Counter(answers)
    return frequency_summary.most_common(1)[0][0]

async def get_final_poe_response(prompt, temperature=0.):
    api_key = API_KEY
    message = ProtocolMessage(role="user", content=prompt)
    retry = 0
    SUCCESS = False
    response = ''
    while not SUCCESS:
        chunks: list[str] = []
        response = ''
        try:
            async for partial in get_bot_response(messages=[message], bot_name=LLM_MODEL, api_key=api_key,
                                                    temperature=temperature):
                if isinstance(partial, MetaMessage):
                    continue
                if partial.is_suggested_reply:
                    continue
                if partial.is_replace_response:
                    chunks.clear()
                chunks.append(partial.text)
            if not chunks:
                raise BotError(f"LLM: sent no response")
            response = "".join(chunks)
            SUCCESS = True
        except Exception as err:
            #print(err)
            await asyncio.sleep(.1)
            retry += 1
            if retry >= 5:
                print("Querying bot failed for 5 times!")
                return response
    return response

#response  = asyncio.run(get_final_poe_response('Hi how are you'))
#print(response)