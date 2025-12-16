from typing import Any
from django.http import HttpRequest

from ninja.security import APIKeyCookie
from ninja_extra import NinjaExtraAPI
from ninja_jwt.authentication import JWTAuth, JWTBaseAuthentication


class JWTCookieAuth(APIKeyCookie, JWTBaseAuthentication):
    param_name = "token"
    
    def authenticate(self, request: HttpRequest, key: str) -> Any:
        return self.jwt_authenticate(request, key)



api = NinjaExtraAPI(
    title="Oxiliere HR API",
    description="API for Oxiliere HR",
    version="1.0.0",
    auth=[JWTAuth(), JWTCookieAuth()],
)



api.register_controllers(
    # controllers here...
)
