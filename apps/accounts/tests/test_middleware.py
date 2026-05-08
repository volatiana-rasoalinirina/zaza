from django.test.client import RequestFactory
from django.test.testcases import TestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.middleware import TenantMiddleware
from apps.accounts.serializers import CustomTokenObtainPairSerializer
from apps.factories import SchoolFactory, UserFactory


class TestTenantMiddleware(TestCase):

    def test_valid_token(self):
        school = SchoolFactory()
        user = UserFactory(school=school)
        token = str(CustomTokenObtainPairSerializer.get_token(user).access_token)
        request = RequestFactory().get('/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        TenantMiddleware(get_response=lambda request: request)(request)
        self.assertEqual(request.school_id, user.school_id)

    def test_no_token_sets_school_id_to_none(self):
        request = RequestFactory().get('/')
        TenantMiddleware(get_response=lambda request: request)(request)
        self.assertIsNone(request.school_id)

    def test_token_without_school_id_sets_none(self):
        user = UserFactory(school=None)
        token = str(RefreshToken.for_user(user).access_token)
        request = RequestFactory().get('/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        TenantMiddleware(get_response=lambda request: request)(request)
        self.assertIsNone(request.school_id)
