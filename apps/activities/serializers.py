from rest_framework import serializers

from .models import Activity


class ActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Activity
        fields = ['id', 'child', 'type', 'note', 'photo_url', 'timestamp', 'picked_up_by', 'logged_by']
        read_only_fields = ['logged_by']

    def validate(self, data):
        if data.get('type') == Activity.Type.CHECKOUT and not data.get('picked_up_by'):
            raise serializers.ValidationError({'picked_up_by': 'Obligatoire pour un départ (CHECKOUT).'})
        return data
