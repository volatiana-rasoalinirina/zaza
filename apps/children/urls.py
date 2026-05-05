from django.urls import path

from apps.children.views import ChildCreateView, GroupCreateView

urlpatterns = [
    path('groups/', GroupCreateView.as_view(), name='group_create'),
    path('children/', ChildCreateView.as_view(), name='child_create'),
]
