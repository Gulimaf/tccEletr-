from django.http import JsonResponse 
class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        response["Content-Security-Policy"] = (
            "default-src 'self'; "

            "script-src 'self' 'unsafe-inline' "
            "https://sdk.mercadopago.com "
            "https://http2.mlstatic.com "
            "https://unpkg.com "
            "https://www.melhorenvio.com.br; "

            "style-src 'self' 'unsafe-inline' "
            "https://fonts.googleapis.com; "

            "font-src 'self' data: "
            "https://fonts.gstatic.com; "

            "img-src 'self' data: blob: "
            "https://*.mercadopago.com "
            "https://*.mercadolibre.com "
            "https://*.mercadolivre.com "
            "https://*.mlstatic.com "
            "https://sandbox.melhorenvio.com.br "
            "https://www.melhorenvio.com.br; "

            "connect-src 'self' "
            "https://api.mercadopago.com "
            "https://api.mercadolibre.com "
            "https://www.mercadolibre.com "
            "https://www.mercadolivre.com "
            "https://http2.mlstatic.com "
            "https://sdk.mercadopago.com "
            "https://unpkg.com "
            "https://servicodados.ibge.gov.br "
            "https://viacep.com.br "
            "https://*.mercadopago.com "
            "https://*.mercadolibre.com "
            "https://*.mercadolivre.com "
            "https://*.mlstatic.com; "

            "frame-src 'self' "
            "https://*.mercadopago.com "
            "https://*.mercadolibre.com "
            "https://*.mercadolivre.com; "

            "form-action 'self' "
            "https://*.mercadopago.com "
            "https://*.mercadolibre.com "
            "https://*.mercadolivre.com; "

            "worker-src 'self' blob:; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "frame-ancestors 'self';"
        )

        response["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "interest-cohort=()"
        )

        response["Strict-Transport-Security"] = (
            "max-age=31536000; "
            "includeSubDomains; "
            "preload"
        )

        return response



class Custom429Middleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 429:
            return JsonResponse(
                {"status": "erro", "mensagem": "Por favor, aguarde um momento antes de tentar novamente."},
                status=429
            )
        return response
