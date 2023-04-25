import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger('app')


class HomeConsumer(AsyncWebsocketConsumer):

    async def websocket_connect(self, event):
        logger.debug('websocket_connect')
        logger.debug(event)
        await self.channel_layer.group_add(
            "home_group",
            self.channel_name,
        )
        await self.accept()

    async def websocket_send(self, event):
        logger.debug('websocket_send')
        logger.debug(event)
        if self.scope["client"][1] is None:
            logger.debug('client 1 is None')
            return
        await self.send(text_data=event['text'])
