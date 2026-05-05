from rest_framework import serializers

from apps.children.models import Child, Group


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = ['id', 'first_name', 'last_name', 'birth_date', 'group']

    def validate_group(self, group):
        request = self.context['request']
        if group.school != request.user.school:
            raise serializers.ValidationError("Ce groupe n'appartient pas à votre école.")
        return group
