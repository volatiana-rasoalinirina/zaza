from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.serializers import CustomTokenObtainPairSerializer


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer