from django.http import JsonResponse
from .services import UserService

class JWTAuthenticationMiddleware:
    """Middleware для аутентификации через JWT токены"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Пропускаем health check и admin
        if request.path in ['/health/', '/admin/']:
            return self.get_response(request)

        # Извлекаем токен
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return JsonResponse({'error': 'Authentication required'}, status=401)

        if not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Invalid token format'}, status=401)

        token = auth_header.split(' ')[1]

        # Проверяем токен через user-service
        user_data = UserService.get_user_from_token(token)
        if not user_data:
            return JsonResponse({'error': 'Invalid token'}, status=401)

        # Заполняем request данными пользователя
        request.user_id = user_data['id']
        request.user_email = user_data['email']
        request.user_data = user_data

        return self.get_response(request)
