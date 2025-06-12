import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class EarningConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f"earnings_{self.user_id}"
        if str(self.scope['user'].id) != str(self.user_id):
            await self.close()
            return
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def earning_notification(self, event):
        await self.send_json({
            'type': 'earning_notification',
            'earning': event['earning']
        })
