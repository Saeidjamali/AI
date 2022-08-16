import logging
import json
from typing import Any, Awaitable, Callable, Dict, Iterable, List, Optional, Text

from rasa.core.channels.channel import InputChannel, OutputChannel, UserMessage, CollectingOutputChannel
import rasa.shared.utils.io
from sanic import Blueprint, response
from sanic.request import Request
# WebSocket
import asyncio
import websockets
from websockets import client
# mongodb

logger = logging.getLogger(__name__)


class WebSocket(InputChannel):
    """A websocket input channel."""

    @classmethod
    def name(cls) -> Text:
        return "WebSocket"

    def __init__(
        self,
    ):
        pass

    def blueprint(
        self, on_new_message: Callable[[UserMessage], Awaitable[Any]]
    ) -> Blueprint:
        ws_server_webhook = Blueprint("websocket_webhook")

        # @ws_server_webhook.listener('after_server_start')
        # async def setup_db(app, loop):
        #     app.ws = WebSocketClient(on_new_message)
        #     # Start connection and get client connection protocol
        #     await asyncio.gather(app.ws.connect())
        #     # Start listener and heartbeat
        #     heart_task = asyncio.create_task(app.ws.heartbeat())
        #     message_task = asyncio.create_task(
        #         app.ws.receiveMessage())

        #     await heart_task
        #     await message_task

        @ws_server_webhook.websocket('/')
        async def health(_: Request, ws) -> None:
            while True:
                logger.debug("HEALTH RUNNING")
                await ws.send("Health is good from rasa")
                return "HEALTH GOOD FROM RASA"

        @ws_server_webhook.websocket('/websocket')
        async def receive(request, ws):
            while True:
                data = await ws.recv()
                data = json.loads(data)
                print(type(data))
                print('Received: {}'.format(data))
                message = data["message"]
                sender_id = data["sender_id"]
                input_channel = self.name()
                print(message)
                print(sender_id)
                collector = CollectingOutputChannel()
                print('it waited on new message')
                await on_new_message(
                UserMessage(
                    message,
                    collector,
                    sender_id,
                    input_channel=input_channel,
                    )
                )
                print("it came here")
                print("Collector Message: ", collector.messages)
                await ws.send(collector.messages[0]['text'])
                data = collector.messages[0]['text']
                print('Sending: ' + data)



        return ws_server_webhook
