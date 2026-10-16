from django.http import JsonResponse


class LicenseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from apps.licensing.state import LICENSE_VALID

        allowed_paths = [
            "/api/license/",
            "/admin/login/",
            "/admin/logout/",
        ]

        if not LICENSE_VALID:
            if not any(request.path.startswith(path) for path in allowed_paths):
                return JsonResponse(
                    {"detail": "License expired. Renewal required."},
                    status=403,
                )

        return self.get_response(request)
