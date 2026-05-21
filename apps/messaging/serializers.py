from rest_framework import serializers

from .models import Message, Thread


class ThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = ['id', 'child', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'sent_at', 'type', 'content']
        read_only_fields = ['sender', 'sent_at']

    def validate(self, data):
        if not data.get('content', '').strip():
            raise serializers.ValidationError({'content': 'A text message must have content.'})
        return data
