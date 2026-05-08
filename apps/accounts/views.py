from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.permissions import IsDirector
from apps.accounts.serializers import CustomTokenObtainPairSerializer, SchoolSerializer


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class SchoolCreateView(generics.CreateAPIView):
    serializer_class = SchoolSerializer
    permission_classes = [IsDirector]

    def perform_create(self, serializer):
        school = serializer.save()
        self.request.user.school = school
        self.request.user.save()