from django.urls import path

from apps.children.views import GroupCreateView

urlpatterns = [
    path('groups/', GroupCreateView.as_view(), name='group_create'),
]
