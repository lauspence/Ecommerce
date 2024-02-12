class CSPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Content-Security-Policy'] = "frame-ancestors 'self' https://*.helcim.app https://*.myhelcim.com"
        return response
