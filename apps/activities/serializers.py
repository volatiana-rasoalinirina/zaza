from rest_framework import serializers

from .models import Activity


class ActivitySerializer(serializers.ModelSerializer):
    type_label = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = ['id', 'child', 'type', 'type_label', 'note', 'photo_url', 'timestamp', 'picked_up_by', 'logged_by']
        read_only_fields = ['logged_by']

    def get_type_label(self, obj):
        return obj.get_type_display()

    def validate(self, data):
        if data.get('type') == Activity.Type.CHECKOUT and not data.get('picked_up_by'):
            raise serializers.ValidationError({'picked_up_by': 'Obligatoire pour un départ (CHECKOUT).'})
        return data
