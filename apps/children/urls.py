from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.children.views import ChildContactViewSet, ChildViewSet, GroupCreateView

router = DefaultRouter()
router.register('children', ChildViewSet, basename='child')
router.register('child-contacts', ChildContactViewSet, basename='childcontact')

urlpatterns = [
    path('groups/', GroupCreateView.as_view(), name='group_create'),
    path('', include(router.urls)),
]
