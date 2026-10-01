from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken

@database_sync_to_async
def get_user_from_token(token):
    User = get_user_model()
    try:
        validated = UntypedToken(token)
        user_id = validated.get("user_id")
        user = User.objects.get(pk=user_id, is_active=True, status="ACTIVE")
        return user
    except (InvalidToken, TokenError, User.DoesNotExist, TypeError, ValueError):
        return None

class QueryStringJWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query = parse_qs(scope.get("query_string", b"").decode())
        tokens = query.get("token", [])
        scope["user"] = await get_user_from_token(tokens[0]) if tokens else None
        return await self.app(scope, receive, send)
