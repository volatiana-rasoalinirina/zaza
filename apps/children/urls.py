from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.children.views import ChildViewSet, GroupCreateView

router = DefaultRouter()
router.register('children', ChildViewSet, basename='child')

urlpatterns = [
    path('groups/', GroupCreateView.as_view(), name='group_create'),
    path('', include(router.urls)),
]
