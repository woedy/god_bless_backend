# consumers.py (inside your app)
import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from celery.result import AsyncResult
from asgiref.sync import sync_to_async

class TaskProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the task_id from the URL
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        
        # Accept the WebSocket connection
        await self.accept()

        # Start the task progress update loop
        await self.send_task_progress()

    async def disconnect(self, close_code):
        # Disconnect the WebSocket connection
        pass

    async def send_task_progress(self):
        # Get the task status using AsyncResult
        task = AsyncResult(self.task_id)
        
        while not task.ready():
            # Check if the task has completed
            await self.send(text_data=json.dumps({
                'state': task.state,
                'progress': task.info.get('progress', 0),
            }))
            
            # Wait before checking again
            await asyncio.sleep(1)
        
        # Task is completed, send final status
        await self.send(text_data=json.dumps({
            'state': task.state,
            'result': task.result,
        }))
