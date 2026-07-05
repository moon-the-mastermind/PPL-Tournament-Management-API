import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import MatchState
from .serializers import MatchStateSerializer


class ScoringConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.match_id = self.scope['url_route']["kwargs"]["match_id"]
        self.room_group_name = f"match_{self.match_id}"


        # join to group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # if connect send current state asap
        match_state = await self.get_match_state()
        if match_state:
            await self.send(text_data = json.dumps({
                "type" : "match_state",
                "data" : match_state
            }))


        async def disconnect(self, close_code):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )



    async def match_update(self, event):
        await self.send(text_data = json.dumps({
            "type" : "match_state",
            "data" : event["data"]

        }))


    @database_sync_to_async
    def get_match_state(self):
        try:
            match_state = MatchState.objects.select_related(
                "striker", "non_striker", "current_bowler"
            ).get(match_id = self.match_id)
            return MatchStateSerializer(match_state).data
        except MatchState.DoesNotExist:
            return None