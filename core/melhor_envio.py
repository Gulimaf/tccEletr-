import requests
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from checkout.models import Pedido
from core.models import MelhorEnvioToken

def obter_token_melhor_envio():
    token = MelhorEnvioToken.objects.first()
    if not token:
        raise Exception("Melhor Envio não está conectado.")
    if token.expires_at > timezone.now() + timedelta(minutes=5):
        return token.access_token
    response = requests.post(
        f"{settings.MELHOR_ENVIO_BASE_URL}/oauth/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": token.refresh_token,
            "client_id": settings.MELHOR_ENVIO_CLIENT_ID,
            "client_secret": settings.MELHOR_ENVIO_CLIENT_SECRET,
        },
        headers={
            "User-Agent": settings.MELHOR_ENVIO_USER_AGENT
        },
        timeout=30
    )
    if response.status_code != 200:
        raise Exception(f"Não foi possível renovar o token do Melhor Envio: {response.text}")
    dados = response.json()
    access_token = dados.get("access_token")
    refresh_token = dados.get("refresh_token")
    expires_in = dados.get("expires_in")
    if not access_token or not expires_in:
        raise Exception("Resposta de renovação do Melhor Envio inválida.")
    token.access_token = access_token
    if refresh_token:
        token.refresh_token = refresh_token
    token.expires_at = (
        timezone.now() +
        timedelta(seconds=int(expires_in))
    )
    token.save(
        update_fields=[
            "access_token",
            "refresh_token",
            "expires_at",
            "atualizado_em",
        ]
    )
    return token.access_token
class MelhorEnvioAPI:
    BASE_URL = settings.MELHOR_ENVIO_BASE_URL
    def __init__(self, access_token=None):
        self.access_token = access_token
    def _headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": settings.MELHOR_ENVIO_USER_AGENT,
        }
    def calcular_frete(self, cep_origem, cep_destino, produtos):
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
        return requests.post(
            f"{self.BASE_URL}/api/v2/me/shipment/calculate",
            headers=self._headers(),
            json=payload,
            timeout=30
        )
    def adicionar_ao_carrinho(self,service,remetente,destinatario,produtos,volumes,options=None):
        payload = {
            "service": service,
            "from": remetente,
            "to": destinatario,
            "products": produtos,
            "volumes": volumes,
            "options": options or {}
        }
        return requests.post(
            f"{self.BASE_URL}/api/v2/me/cart",
            headers=self._headers(),
            json=payload,
            timeout=30
        )
    def comprar_envio(self, order_ids):
        payload = {
            "orders": [
                str(order_id)
                for order_id in order_ids
            ]
        }
        return requests.post(
            f"{self.BASE_URL}/api/v2/me/shipment/checkout",
            headers=self._headers(),
            json=payload,
            timeout=30
        )
    def gerar_etiqueta(self, order_ids):
        payload = {
            "orders": [
                str(order_id)
                for order_id in order_ids
            ]
        }
        return requests.post(
            f"{self.BASE_URL}/api/v2/me/shipment/generate",
            headers=self._headers(),
            json=payload,
            timeout=30
        )
    def imprimir_etiqueta(self, order_ids, mode="private"):
        payload = {
            "orders": [
                str(order_id)
                for order_id in order_ids
            ],
            "mode": mode
        }
        return requests.post(
            f"{self.BASE_URL}/api/v2/me/shipment/print",
            headers=self._headers(),
            json=payload,
            timeout=30
        )
    def rastrear_envio(self, order_ids):
        payload = {
            "orders": [
                str(order_id)
                for order_id in order_ids
            ]
        }
        return requests.post(
            f"{self.BASE_URL}/api/v2/me/shipment/tracking",
            headers=self._headers(),
            json=payload,
            timeout=30
        )
def imprimir_etiqueta_pedido(pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)
    if not pedido.melhor_envio_order_id:
        raise ValueError("O pedido não possui um ID de envio do Melhor Envio.")
    access_token = obter_token_melhor_envio()
    api = MelhorEnvioAPI(access_token=access_token)
    response = api.imprimir_etiqueta(pedido.melhor_envio_order_id)
    if response.status_code not in (200, 201):
        raise ValueError(f"Erro ao imprimir etiqueta no Melhor Envio: {response.text}")
    return response