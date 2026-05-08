from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.children.views import ChildContactViewSet, ChildViewSet, GroupViewSet

router = DefaultRouter()
router.register('groups', GroupViewSet, basename='group')
router.register('children', ChildViewSet, basename='child')
router.register('child-contacts', ChildContactViewSet, basename='childcontact')

urlpatterns = [
    path('', include(router.urls)),
]
