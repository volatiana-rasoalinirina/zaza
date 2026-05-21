from django.urls import include, path
from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter

from .views import MessageViewSet, ThreadViewSet

router = DefaultRouter()
router.register('threads', ThreadViewSet, basename='thread')

threads_router = NestedDefaultRouter(router, 'threads', lookup='thread')
threads_router.register('messages', MessageViewSet, basename='thread-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(threads_router.urls)),
]
