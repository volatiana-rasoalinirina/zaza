import jwt
from django.conf import settings


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.school_id = None
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token_str = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(token_str, settings.SECRET_KEY, algorithms=['HS256'])
                request.school_id = payload.get('school_id')
            except Exception :
                pass
        return self.get_response(request)