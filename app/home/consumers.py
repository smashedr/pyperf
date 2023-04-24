import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger('app')


class HomeConsumer(AsyncWebsocketConsumer):

    async def websocket_connect(self, event):
        logger.debug('websocket_connect')
        await self.channel_layer.group_add(
            "home_group",
            self.channel_name,
        )
        await self.accept()

    async def websocket_receive(self, event):
        logger.debug('websocket_receive')
        logger.debug(event)

    async def websocket_disconnect(self, event):
        # Remove the client from any groups it had previously joined
        for group_name in self.groups:
            await self.channel_layer.group_discard(
                group_name,
                self.channel_name
            )
        self.groups = set()

    async def websocket_send(self, event):
        logger.debug('websocket_send')
        logger.debug(event)
        await self.send(text_data=event['text'])
