from django.test.client import RequestFactory
from django.test.testcases import TestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.middleware import TenantMiddleware
from apps.accounts.models import School, User
from apps.accounts.serializers import CustomTokenObtainPairSerializer


class TestTenantMiddleware(TestCase):
    def test_valid_token(self):
        school = School.objects.create(name='School name', slug='school-name')
        user = User.objects.create_user(email='test@gmail.com', password='<PASSWORD>', school=school)
        refresh_token = CustomTokenObtainPairSerializer.get_token(user)
        token = str(refresh_token.access_token)
        request = RequestFactory().get('/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'

        middleware = TenantMiddleware(get_response=lambda request: request)
        middleware(request)

        self.assertEqual(request.school_id, user.school_id)

    def test_no_token_sets_school_id_to_none(self):
        request = RequestFactory().get('/')
        middleware = TenantMiddleware(get_response=lambda request: request)
        middleware(request)
        self.assertIsNone(request.school_id)

    def test_token_without_school_id_sets_none(self):
        user = User.objects.create_user(email='test2@gmail.com', password='test123')
        token = str(RefreshToken.for_user(user).access_token)
        request = RequestFactory().get('/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        middleware = TenantMiddleware(get_response=lambda request: request)
        middleware(request)
        self.assertIsNone(request.school_id)
