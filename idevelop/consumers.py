from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from idevelop.models import CollabBox
import json


class MyConsumer(WebsocketConsumer):
    group_name = 'idevelop_group'
    channel_name = 'idevelop_channel'
    user = None

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
        )
        self.accept()
        if not self.scope["user"].is_authenticated:
            self.send_error(f'You must be logged in')
            self.close()
            return         

        self.user = self.scope["user"]

        try: collab_box = CollabBox.objects.get(owner = self.scope["user"])
        except CollabBox.DoesNotExist:
            collab_box = CollabBox.objects.create(
            text_value="Nada",
            owner=self.scope["user"],
            )
            collab_box.allowed_editors.add(self.scope["user"])
            collab_box.save

        self.broadcast_list(collab_box.id)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )

    def receive(self, **kwargs):
        if 'text_data' not in kwargs:
            self.send_error('you must send text_data')
            return

        try:
            data = json.loads(kwargs['text_data'])
        except json.JSONDecoder:
            self.send_error('invalid JSON sent to server')
            return

        if 'action' not in data:
            self.send_error('action property not sent in JSON')
            return

        action = data['action']

        if action == 'update':
            self.received_update(data)
            return

        self.send_error(f'Invalid action property: "{action}"')

    def received_update(self, data):
        if 'id' not in data:
            self.send_error('id property not sent in JSON')
            return
        if 'box_id' not in data:
            self.send_error('box_id property not sent in JSON')
            return
        try:
            collab_box = CollabBox.objects.get(id=data['box_id'])
            if not collab_box.allowed_editors.filter(id=data['id']).exists() and not data['id'] == data['owner_id']:
                self.send_error("You don't have the permissions to edit buddy") 
                return
            collab_box.text_value = data['text']
            collab_box.save()
        except CollabBox.DoesNotExist:
            collab_box = CollabBox.objects.create(
            text_value=data['text'],
            owner=self.user,
            )
            collab_box.allowed_editors.add(self.user)
            collab_box.save()
            
        #Update Model To Have The Newest Text
        self.broadcast_list(collab_box.id)

    def send_error(self, error_message):
        self.send(text_data=json.dumps({'type': 'error', 'data': error_message}))

    def broadcast_list(self, collabID):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'broadcast_event',
                'message': json.dumps({
                    'type': 'update',  
                    'data': CollabBox.ready_response(collabID)  
                })
            }
        )

    def broadcast_event(self, event):
        self.send(text_data=event['message'])