import requests
from django.conf import settings
def calcular_frete(token,cep_origem,cep_destino,produtos):
    url = (
        settings.MELHOR_ENVIO_BASE_URL
        + "/api/v2/me/shipment/calculate/"
    )
    payload = {
        "from": {
            "postal_code": cep_origem
        },
        "to": {
            "postal_code": cep_destino
        },
        "products": produtos,
        "options": {
            "receipt": False,
            "own_hand": False
        }
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": (
            f"{settings.MELHOR_ENVIO_USER_AGENT} "
            f"({'gustavo.lfs2009@gmail.com'})"
        )
    }
    response = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=30
    )
    return response