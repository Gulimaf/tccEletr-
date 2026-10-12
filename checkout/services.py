from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from .models import Pedido, PedidoItem, ProdutoCores
from django.urls import reverse
from cart.cart import Cart
from core.models import CotacaoFrete, OpcaoFrete, MelhorEnvioToken
from dotenv import load_dotenv
load_dotenv()
import mercadopago
import os
from django.core.mail import send_mail
from core.melhor_envio import MelhorEnvioAPI, obter_token_melhor_envio
from django.conf import settings 
from cryptography.fernet import Fernet
from django.conf import settings
import base64
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import User
sdk = mercadopago.SDK(os.getenv("SDK"))
def sendEmail(assunto, destinatario, texto, texto_botao, link_botao,username):
    html = render_to_string("message.html", {
        "mensagem_texto": texto,
        "texto_botao": texto_botao,
        "link_botao": link_botao,
        "nome": username,
    })
    texto_simples = f"{texto}\nAcesse: {link_botao}"
    email = EmailMultiAlternatives(
        subject=assunto,
        body=texto_simples,
        from_email="gustavo.lfs2009@gmail.com",
        to=[destinatario],
    )
    email.attach_alternative(html, "text/html")
    try:
        email.send(fail_silently=False)
        print("EMAIL ENVIADO COM SUCESSO")
        return True
    except Exception as e:
        print("ERRO AO ENVIAR EMAIL:", e)
        return False
        
def validar_frete_selecionado(request):
    frete = request.session.get("frete_selecionado")
    if not frete:
        return False, None, None, "Nenhum frete selecionado."
    try:
        cotacao = CotacaoFrete.objects.get(id=frete["cotacao_id"],ativa=True)
        opcao = OpcaoFrete.objects.get(id=frete["opcao_id"],cotacao=cotacao)
    except (CotacaoFrete.DoesNotExist,OpcaoFrete.DoesNotExist):
        return False, None, None, "Frete inválido."
    if cotacao.expira_em < timezone.now():
        return False, None, None, "A cotação do frete expirou."
    cart = Cart(request)
    if cart.get_cart_hash() != cotacao.carrinho_hash:
        return (False,None, None,"O carrinho foi alterado. Calcule o frete novamente.")
    return True, cotacao, opcao, None
    
@transaction.atomic
def criar_pedido(request, dados_cliente):
    cart = Cart(request)
    itens = cart.get_produtos()
    if not itens:
        raise ValueError("O carrinho está vazio.")
    metodo_entrega = request.session.get(
        "metodo_entrega",
        "frete"
    )
    if metodo_entrega == "frete":
        sucesso, cotacao, opcao, erro = validar_frete_selecionado(request)
        if not sucesso:
            raise ValueError(erro)
        frete = Decimal(str(opcao.preco))
        transportadora = opcao.transportadora_nome
        servico_frete = opcao.nome
        prazo_frete = opcao.prazo
        cotacao_frete_id = cotacao.id
        opcao_frete_id = opcao.id
    else:
        metodo_entrega = "retirada"
        frete = Decimal("0.00")
        transportadora = ""
        servico_frete = ""
        prazo_frete = None
        cotacao_frete_id = None
        opcao_frete_id = None
    subtotal = sum(Decimal(str(item["subtotal"])) for item in itens)
    total = subtotal + frete
    pedido = Pedido.objects.create(
        usuario=request.user,
        nome_cliente=dados_cliente["nome"],
        email_cliente=dados_cliente["email"],
        telefone_cliente=dados_cliente["telefone"],
        cep=dados_cliente["cep"],
        endereco=dados_cliente["endereco"],
        numero=dados_cliente["numero"],
        complemento=dados_cliente.get("complemento", ""),
        bairro=dados_cliente["bairro"],
        cidade=dados_cliente["cidade"],
        estado=dados_cliente["estado"],
        subtotal=subtotal,
        frete=frete,
        total=total,
        transportadora=transportadora,
        servico_frete=servico_frete,
        prazo_frete=prazo_frete,
        cotacao_frete_id=cotacao_frete_id,
        opcao_frete_id=opcao_frete_id,
        status="aguardando_pagamento",
        metodo_entrega=metodo_entrega
    )
    for item in itens:
        PedidoItem.objects.create(
            pedido=pedido,
            produto=item["produto"],
            cor=item["cor"],
            quantidade=item["quantidade"],
            preco_unitario=Decimal(
                str(item["preco"])
            ),
            subtotal=Decimal(
                str(item["subtotal"])
            )
        )
    return pedido
def enviar_email_confirmacao_pedido(pedido, link_acompanhamento=None):
    assunto = f"Pedido #{pedido.id} confirmado - Cerâmica Barroá"
    if not link_acompanhamento:
        link_acompanhamento = f"https://ceramicabarroa.com.br/perfil/"
    context = {
        'pedido': pedido,
        'nome': pedido.nome_cliente,
        'itens': pedido.itens.select_related("produto", "cor"),
        'link_botao': link_acompanhamento,
        'texto_botao': 'Ver Detalhes do Pedido',
        'site_url': 'https://ceramicabarroa.com.br',
    }
    html_content = render_to_string('confirmacao_pedido.html', context)
    text_content = strip_tags(html_content) 
    email = EmailMultiAlternatives(
        subject=assunto,
        body=text_content,
        from_email=os.getenv("EMAIL_HOST_USER"),
        to=[pedido.email_cliente],
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)
def criar_envio_melhor_envio(pedido_id):
    pedido = (Pedido.objects.prefetch_related(
            "itens__produto",
            "itens__cor"
        ).get(id=pedido_id)
    )
    if pedido.opcao_frete_id is None:
        return
    access_token = obter_token_melhor_envio()
    if not access_token: 
        raise ValueError("Melhor Envio não está conectado.")
    api = MelhorEnvioAPI(access_token=access_token)
    produtos = []
    for item in pedido.itens.all():
        produtos.append({
            "name": str(item.produto),
            "quantity": str(item.quantidade),
            "unitary_value": str(item.preco_unitario),
        })
    documento = descriptografar_documento(pedido.usuario.perfil.documento)
    cep = "".join(
        c for c in str(pedido.cep)
        if c.isdigit()
    )
    destinatario = {
        "name": pedido.nome_cliente,
        "document": documento,
        "email": pedido.email_cliente,
        "phone": pedido.telefone_cliente,
        "address": pedido.endereco,
        "number": pedido.numero,
        "complement": pedido.complemento,
        "district": pedido.bairro,
        "city": pedido.cidade,
        "postal_code": cep,
        "state_abbr": pedido.estado,
        "country_id": "BR",
    }
    remetente = {
        "name": settings.MELHOR_ENVIO_FROM_NAME,
        "email": settings.MELHOR_ENVIO_FROM_EMAIL,
        "phone": settings.MELHOR_ENVIO_FROM_PHONE,
        "document": settings.MELHOR_ENVIO_FROM_DOCUMENT,
        "address": settings.MELHOR_ENVIO_FROM_ADDRESS,
        "number": settings.MELHOR_ENVIO_FROM_NUMBER,
        "district": settings.MELHOR_ENVIO_FROM_DISTRICT,
        "city": settings.MELHOR_ENVIO_FROM_CITY,
        "postal_code": settings.MELHOR_ENVIO_FROM_POSTAL_CODE,
        "state_abbr": settings.MELHOR_ENVIO_FROM_STATE,
    }
    opcao = OpcaoFrete.objects.get(id=pedido.opcao_frete_id)
    options = {
        "platform": "Cerâmica Barroá",
        "reminder": f"Pedido #{pedido.id}",
        "insurance_value": float(pedido.subtotal),
        "receipt": False,
        "own_hand": False,
        "tags": [
            {
                "tag": str(pedido.id),
                "url": None
            }
        ]
    }
    volumes = []
    for item in pedido.itens.all():
        produto = item.produto
        volumes.append({
            "height": float(produto.altura),
            "width": float(produto.largura),
            "length": float(produto.comprimento),
            "weight": float(produto.peso),
        })
    response = api.adicionar_ao_carrinho(
        service=opcao.service_id,
        remetente=remetente,
        destinatario=destinatario,
        produtos=produtos,
        volumes=volumes,
        options=options
    )
    if response.status_code != 201:
        raise ValueError(
            f"Erro ao adicionar envio ao Melhor Envio: "
            f"{response.text}"
        )
    dados = response.json()
    pedido.melhor_envio_order_id = dados["id"]
    pedido.save(update_fields=["melhor_envio_order_id"])

def enviar_email_novo_pedido_staff(pedido):
    staffs = User.objects.filter(
        is_staff=True,
        is_active=True
    ).exclude(
        email=""
    )
    for staff in staffs:
        sendEmail(
            assunto=f"Novo pedido pago #{pedido.id}",
            destinatario=staff.email,
            texto=(
                f"O pedido #{pedido.id} foi pago "
                "e está aguardando processamento."
            ),
            texto_botao="Ver pedido no admin",
            link_botao=f"https://ceramicabarroa.com.br/perfil/",
            username=staff.username
        )
@transaction.atomic
def processar_pagamento_aprovado(pedido, payment):
    if pedido.status != "aguardando_pagamento":
        return False
    if pedido.status == "pago":
        return
    pedido.status = "pago"
    pedido.mp_payment_id = str(payment.get("id"))
    pedido.mp_status = payment.get("status")
    pedido.mp_status_detail = payment.get("status_detail")
    pedido.data_pagamento = timezone.now()
    pedido.atualizado_em = timezone.now()
    pedido.save(update_fields=[
        "status",
        "mp_payment_id",
        "mp_status",
        "mp_status_detail",
        "data_pagamento",
        "atualizado_em",
    ])
    for item in pedido.itens.select_related("cor"):
            cor = ProdutoCores.objects.select_for_update().get(id_cor=item.cor.id_cor)
            if cor.quantidade < item.quantidade:
                raise ValueError(
                    f"Estoque insuficiente para {item.produto}"
                )
            cor.quantidade -= item.quantidade
            cor.save(update_fields=["quantidade"])
    transaction.on_commit(lambda: enviar_email_confirmacao_pedido(pedido))
    transaction.on_commit(lambda: enviar_email_novo_pedido_staff(pedido))
    transaction.on_commit(lambda: criar_envio_melhor_envio(pedido.id))
    return True

_raw_key = base64.urlsafe_b64decode(settings.FIELD_ENCRYPTION_KEY.encode())
fernet = Fernet(base64.urlsafe_b64encode(_raw_key))
def criptografar_documento(documento):
    return fernet.encrypt(documento.encode()).decode()

def descriptografar_documento(documento):
    return fernet.decrypt(documento.encode()).decode()
def comprar_e_gerar_etiqueta(pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)
    if not pedido.melhor_envio_order_id:
        raise ValueError(
            "O pedido não possui um ID de envio do Melhor Envio."
        )
    token = MelhorEnvioToken.objects.first()
    if not token:
        raise ValueError(
            "Melhor Envio não está conectado."
        )
    api = MelhorEnvioAPI( access_token=token.access_token)
    order_id = pedido.melhor_envio_order_id
    response_compra = api.comprar_envio([order_id])
    if response_compra.status_code not in (200, 201):
        raise ValueError(
            f"Erro ao comprar envio no Melhor Envio: {response_compra.text}"
        )
    response_etiqueta = api.gerar_etiqueta([order_id])
    if response_etiqueta.status_code not in (200, 201):
        raise ValueError(
            f"Erro ao gerar etiqueta no Melhor Envio: {response_etiqueta.text}"
        )
    pedido.status = "etiqueta_gerada"
    pedido.save(update_fields=["status"])
    return response_etiqueta.json()
def atualizar_tracking_pedido(pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)
    if not pedido.melhor_envio_order_id:
        raise ValueError(
            "O pedido não possui um ID de envio do Melhor Envio."
        )
    access_token = obter_token_melhor_envio()
    if not access_token:
        raise ValueError(
            "Melhor Envio não está conectado."
        )
    api = MelhorEnvioAPI(access_token=access_token)
    response = api.rastrear_envio([pedido.melhor_envio_order_id])
    if response.status_code != 200:
        raise ValueError(
            "Erro ao consultar rastreamento no Melhor Envio: "
            f"{response.text}"
        )
    dados = response.json()
    order_id_str = str(pedido.melhor_envio_order_id)
    if order_id_str not in dados:
        raise ValueError(
            "O envio não foi encontrado no rastreamento do Melhor Envio."
        )
    info_envio = dados[order_id_str]
    rastreio_cod = info_envio.get("melhorenvio_tracking")
    if rastreio_cod:
        pedido.codigo_rastreio = rastreio_cod
    status_me = info_envio.get("status")
    print("STATUS MELHOR ENVIO:", status_me)
    print("DADOS RASTREAMENTO:", info_envio)
    mapa_status = {
        "posted": "enviado",
        "delivered": "entregue",
    }
    novo_status = mapa_status.get(status_me)
    if novo_status:
        pedido.status = novo_status
    pedido.save(
        update_fields=[
            "codigo_rastreio",
            "status",
            "atualizado_em",
        ]
    )
    return dados