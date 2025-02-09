from freezegun import freeze_time
from datetime import datetime

class DateOverrideMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        with freeze_time("2024-09-05"):
            response = self.get_response(request)
        return response
