from django.conf import settings
from django.http import HttpResponse


class CorsMiddleware:
    allowed_methods = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    allowed_headers = "Content-Type"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "OPTIONS":
            response = HttpResponse(status=200)
        else:
            response = self.get_response(request)
        origin = request.headers.get("Origin")
        if origin not in settings.FRONTEND_ORIGINS:
            origin = settings.FRONTEND_ORIGINS[0]
        response["Access-Control-Allow-Origin"] = origin
        response["Access-Control-Allow-Methods"] = self.allowed_methods
        response["Access-Control-Allow-Headers"] = self.allowed_headers
        response["Vary"] = "Origin"
        return response
