from rest_framework import serializers

from apps.children.models import Child, ChildContact, Group

from django.utils.translation import gettext_lazy as _


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = ['id', 'first_name', 'last_name', 'birth_date', 'group', 'allergies']

    def validate_group(self, group):
        request = self.context['request']
        if group.school != request.user.school:
            raise serializers.ValidationError(_("Ce groupe n'appartient pas à votre école."))
        return group


class ChildContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildContact
        fields = ['id', 'child', 'name', 'phone', 'relation', 'photo_url', 'is_authorized_pickup', 'is_emergency_contact']

    def validate_child(self, child):
        request = self.context['request']
        if child.school != request.user.school:
            raise serializers.ValidationError(_("Cet enfant n'appartient pas à votre école."))
        return child

    def validate(self, data):
        is_pickup = data.get('is_authorized_pickup', getattr(self.instance, 'is_authorized_pickup', False))
        is_emergency = data.get('is_emergency_contact', getattr(self.instance, 'is_emergency_contact', False))
        if not is_pickup and not is_emergency:
            raise serializers.ValidationError(_("Le contact doit être au moins un pickup autorisé ou un contact d'urgence."))
        return data
