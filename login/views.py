from django.shortcuts import render
from django.shortcuts import render, get_object_or_404,redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse, Http404
from .models import Perfil
from core.models import Produtos, ProdutoCores, ProdutoImagens
from checkout.models import Pedido
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.safestring import mark_safe
from login.utils.token_generator import token_generator
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
import json
from checkout.services import criptografar_documento
from .services import consultar_cep
from core.models import MelhorEnvioToken
from django_smart_ratelimit import ratelimit
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
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

@ratelimit(key="ip",rate="10/10m",block=True,skip_if=lambda request: request.method != "POST")
def register(request):
    if request.method == "GET":
        return render(request, "cadastro.html")
    if request.method == "POST":
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        password = request.POST.get('password')
        user = User.objects.filter(username=nome).exists()
        emailUser = User.objects.filter(email=email).exists()
        if emailUser:
            login_url = reverse('login')
            messages.error(request,mark_safe(f'Já existe uma conta com esse email. <a href="{login_url}">Fazer login</a>'))
            return redirect('register')
        user = User.objects.create_user(username=nome, email=email, password=password,is_active=False)
        token = token_generator.make_token(user)
        path = reverse('confirmar-email', args=[user.pk, token])
        link = request.build_absolute_uri(path)
        enviado = sendEmail(assunto="Confirme seu cadastro",
                  destinatario=email,
                  texto="Clique no botão abaixo para confirmar seu cadastro",
                  texto_botao="Confirmar email",
                  link_botao=link,
                  username=user.username)
        if enviado:
            userPerfil = Perfil.objects.create(
                user=user,
                telefone=telefone,
            )
            user.is_active = False
            user.save()
            messages.success(request,('verifique seu email para ativar sua conta'))
            return redirect('register')
        else:
            user.delete()
            messages.error(request, "Não foi possível enviar o email de confirmação.")
            return redirect('register')

@ratelimit(key="ip",rate="20/10m",block=True,skip_if=lambda request: request.method != "GET")
def confirmarEmail(request,user_id,token):
    if request.method == "GET":
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            messages.error(request,'Usuário não encontrado, tente fazer o cadastro novamente')
            return render(request, 'cadastro.html')
        resultado = token_generator.check_token(user, token)
        if not token_generator.check_token(user, token):
            messages.error(request,'Token inexistente mande o email de novo')
            return redirect('reenviar-confirmacao')
        else:
            user.is_active = True
            user.save()
            return render(request, 'emailConfirmado.html')

@ratelimit(key="ip",rate="12/4m",block=True,skip_if=lambda request: request.method != "POST")
def loginF(request):
    if request.method == "GET":
        return render(request, "login.html")
    if request.method == "POST":
        email = request.POST.get('email')
        senha = request.POST.get('password')
        user = User.objects.filter(email=email).first()
        if user is None or not user.check_password(senha):
            messages.error(request, 'Usuário ou senha inválidos')
            return render(request,'login.html')
        if not user.is_active:
            request.session['email_confirmacao'] = user.email
            return redirect('reenviar-confirmacao')
        login(request,user)
        return redirect('homePerfil')
    
@ratelimit(key="ip",rate="3/10m",block=True,skip_if=lambda request: request.method != "POST")
def reenviarConfirmacao(request):
    if request.method == "GET":
        return render(request,'precisaConfirmar.html')
    if request.method == "POST":
        email = request.session.get('email_confirmacao')
        user = User.objects.filter(email=email).first()
        if not email:
            return JsonResponse({
                "status" : "erro",
                "mensagem" : "Sem email válido"
            })
        if not user:
            return JsonResponse({
                "status" : "erro",
                "mensagem" : "Usuário não encontrado tente fazer o cadastro novamente"
            })
        if user.is_active:
            return JsonResponse({
                "status" : "erro",
                "mensagem" : "Email já confirmado."
            })
        token = token_generator.make_token(user)
        link = request.build_absolute_uri(
            f"/confirmar-email/{user.pk}/{token}/"
        )
        sendEmail(
            assunto="Confirme seu cadastro",
            destinatario=email,
            texto="Clique no botão abaixo para confirmar seu cadastro:",
            texto_botao="Confirmar e-mail",
            link_botao=link,
            username=user.username
        )
        messages.success(request, 'Email enviado com sucesso')
        return render(request,'precisaConfirmar.html')

def validar_cpf(cpf):
    cpf = ''.join(
        c for c in cpf
        if c.isdigit()
    )
    if len(cpf) != 11:
        return False
    if cpf == cpf[0] * 11:
        return False
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = soma % 11
    if resto < 2:
        primeiro_digito = 0
    else:
        primeiro_digito = 11 - resto
    if int(cpf[9]) != primeiro_digito:
        return False
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = soma % 11
    if resto < 2:
        segundo_digito = 0
    else:
        segundo_digito = 11 - resto
    if int(cpf[10]) != segundo_digito:
        return False
    return True

@ratelimit(key="user",rate="60/m",block=True,skip_if=lambda request: request.method != "GET")
@login_required(login_url="/login/")
def loadPerfil(request):
    if not request.user.is_active:
        return redirect('precisaConfirmar')
    if request.user.is_staff and request.method == "GET":
        melhor_envio_token = MelhorEnvioToken.objects.first()
        return render(request, 'perfilStaff.html',{
            "melhor_envio_token": melhor_envio_token,
        })
    if request.method == "GET" and not request.user.is_staff:
        perfil = Perfil.objects.get(user=request.user)
        cpf_cadastrado = bool(perfil.documento)
        pedidos = (Pedido.objects.filter(usuario=request.user).prefetch_related(
            "itens__produto",
            "itens__cor",
            "itens__produto__produtoimagens_set"
        ).order_by("-criado_em"))
        for pedido in pedidos:
            for item in pedido.itens.all():
                categoria = item.produto.categoria
                if categoria:
                    item.nome_produto = categoria.split(",")[0].strip()
                else:
                    item.nome_produto = "Produto"
                if item.cor:
                    item.nome_cor = item.cor.nome
                else:
                    item.nome_cor = "Sem cor"
                item.imagem_produto = (
                    item.produto.produtoimagens_set.first()
                )
        return render(request,"perfil.html",{
                "perfil": perfil,
                "cpf_cadastrado": cpf_cadastrado,
                "pedidos" : pedidos,
            })
    if request.method == "POST" and not request.user.is_staff:
        perfil = Perfil.objects.get(user=request.user)
        documento = request.POST.get("cpf", "").strip()
        cep = request.POST.get("cep", "").strip()
        endereco = request.POST.get("logradouro", "").strip()
        numero = request.POST.get("numero", "").strip()
        complemento = request.POST.get("complemento", "").strip()
        bairro = request.POST.get("bairro", "").strip()
        cidade = request.POST.get("cidade", "").strip()
        estado = request.POST.get("estado", "").strip()
        if documento:
            if perfil.documento:
                messages.error(request,"O CPF já foi cadastrado e não pode ser alterado.")
                return redirect("homePerfil")
        if not perfil.documento:
            if not documento:
                messages.error(request,"O CPF é obrigatório.")
                return redirect("homePerfil")
            documento = "".join(
                    c for c in documento
                    if c.isdigit()
                )
            if len(documento) != 11:
                messages.error(request,"CPF inválido.")
                return redirect("perfil")
            if not validar_cpf(documento):
                messages.error(request,"CPF inválido.")
                return redirect("perfil")
            documentoC = criptografar_documento(documento)
            perfil.documento = documentoC
        else:
            pass
        if not all([cep,endereco,numero,bairro,cidade,estado]):
            messages.error(request,"Preencha todas as informações obrigatórias.")
            return redirect("homePerfil")
        dados_cep = consultar_cep(cep)
        if not dados_cep:
            messages.error(request,"CEP inválido ou não encontrado.")
            return redirect("homePerfil")
        estado_cep = dados_cep.get("uf", "").strip().upper()
        cidade_cep = dados_cep.get("localidade", "").strip()
        if estado != estado_cep:
            messages.error(request,"O estado selecionado não corresponde ao CEP informado.")
            return redirect("homePerfil")
        if cidade.lower() != cidade_cep.lower():
            messages.error(request,"A cidade selecionada não corresponde ao CEP informado.")
            return redirect("homePerfil")
        perfil.cep = cep
        perfil.endereco = endereco
        perfil.numero = numero
        perfil.complemento = complemento
        perfil.bairro = bairro
        perfil.cidade = cidade
        perfil.estado = estado
        perfil.save()
        messages.success(request,"Informações salvas.")
        return redirect("homePerfil")

@ratelimit(key="user",rate="30/m",block=True,skip_if=lambda request: request.method != "POST")
def logoutF(request):
    if request.method == "POST":
        logout(request)
        return redirect('home')
    if request.method == "GET":
        return redirect('home')
    
@ratelimit(key="ip",rate="5/15m",block=True,skip_if=lambda request: request.method != "POST")
def redefinirSenha(request):
    if request.method == "GET":
        return render(request, 'email.html')
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Email não encontrado")
            return render(request, 'email.html')
        token = token_generator.make_token(user)
        link = request.build_absolute_uri(
        reverse('redefinirSenhap2', kwargs={'user_id': user.pk, 'token': token}))
        sendEmail(
            assunto="Redefinição de Senha",
            destinatario=email,
            texto="Clique no botão abaixo para redefinir a sua senha:",
            texto_botao="Redefinir Senha",
            link_botao=link,
            username=user.username
        )
        messages.success(request, 'Email enviado')
        return render(request, 'email.html')

@ratelimit(key="ip",rate="5/15m",block=True,skip_if=lambda request: request.method != "POST")
def resetPassword(request, user_id, token):
    if request.method == 'GET':
        return render(request, 'forgotPass.html')
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Usuário inexistente, tente fazer o processo novamente')
        return render(request, 'forgotPass.html')
    if not token_generator.check_token(user, token):
        messages.error(request, 'token inválido envie o email novamente')
        return render(request, 'forgotPass.html')
    novaSenha = request.POST.get('novaSenha')
    repeatedNovaSenha = request.POST.get('repeatedNovaSenha')
    if not novaSenha or not repeatedNovaSenha:
        messages.error(request, 'Por favor, preencha todos os campos.')
        return render(request, 'forgotPass.html')
    if novaSenha != repeatedNovaSenha:
        messages.error(request, 'As senhas não coincidem. Tente novamente.')
        return render(request, 'forgotPass.html')
    user.set_password(novaSenha)
    user.save()
    login_url = reverse('login')
    messages.success(request, mark_safe(
        f'Senha alterada com sucesso <a href="{login_url}">Fazer login</a>'
    ))
    return render(request, 'forgotPass.html')

@ratelimit(key="ip",rate="20/10m",block=True,skip_if=lambda request: request.method != "POST")
def cadProduto(request,id_produto=None):
    if not request.user.is_staff:
        raise Http404()
    if request.method == "GET":
        raise Http404()
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({'erro':'Corpo da requisição inválido'}, status=400)
        id = data.get('id')
        codigo = data.get('codigo')
        is_sale = data.get('is_sale')
        valorPromocao = data.get('valorPromocao')
        valor = data.get('valor')
        altura = data.get('altura')
        largura = data.get('largura')
        comprimento = data.get('comprimento')
        volume = data.get('volume')
        categoria = data.get('categoria')
        ativo = data.get('ativo')
        peso = data.get('peso')
        descricao = data.get('descricao')
        if all([codigo,descricao,valor,categoria]):
            try:
                Produtos.objects.create(
                    descricao=descricao,
                    valor=valor,
                    is_sale=is_sale,
                    sale_value=valorPromocao,
                    codigo=codigo,
                    categoria=categoria,
                    ativo=ativo,
                    altura=altura,
                    largura=largura,
                    comprimento=comprimento,
                    volume=volume,
                    peso=peso
                )
                return JsonResponse({
                    'status': 'ok',
                    'redirect_url' : reverse('homePerfil')
                })
            except Exception as e: 
                return JsonResponse({
                'status': 'erro',
                'redirect_url': reverse('home') 
                })
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({'status':'erro','mensagem':'Corpo da requisição inválido'}, status=400)
        id = data.get('id')
        codigo = data.get('codigo')
        valor = data.get('valor')
        is_sale = data.get('is_sale')
        valorPromocao = data.get('valorPromocao')
        altura = data.get('altura')
        largura = data.get('largura')
        comprimento = data.get('comprimento')
        volume = data.get('volume')
        categoria = data.get('categoria')
        ativo = data.get('ativo')
        peso = data.get('peso')
        descricao = data.get('descricao')
        try:
            Produtos.objects.filter(id_produto=id).update(
                descricao=descricao,
                valor=valor,
                is_sale=is_sale,
                sale_value=valorPromocao,
                codigo=codigo,
                categoria=categoria,
                ativo=ativo,
                altura=altura,
                largura=largura,
                comprimento=comprimento,
                volume=volume,
                peso=peso
            )
            return JsonResponse({
                'status': 'ok',
                'mensagem' : 'Produto atualizado.',
                'redirect_url' : reverse('homePerfil')
            })
        except: 
            return JsonResponse({
            'status': 'erro',
            'mensagem': 'Erro ao atualizar produto.',
            'redirect_url': reverse('home') 
            })
    if request.method == 'DELETE':
        try:
            produto = get_object_or_404(Produtos, id_produto=id_produto)
            imagens = ProdutoImagens.objects.filter(codigo=produto)
            for img in imagens:
                if img.imagem:
                    img.imagem.delete(save=False)
            imagens.delete()
            ProdutoCores.objects.filter(codigo=produto).delete()
            produto.delete()
            return JsonResponse({
                'status': 'ok',
                'redirect_url' : reverse('homePerfil')
            })
        except Exception as e: 
            # print(e)
            return JsonResponse({
            'status': 'erro',
            'redirect_url': reverse('home') 
            })

@ratelimit(key="ip",rate="20/10m",block=True,skip_if=lambda request: request.method != "POST")
def cadastrar_cor(request,id_cor=None):
    if not request.user.is_staff:
        raise Http404()
    if request.method == "POST":
        try:
            dados = json.loads(request.body)
        except:
            return JsonResponse({"status":"erro","mensagem": "Corpo da requisição inválido."}, status=400)
        try:
            produto = Produtos.objects.get(codigo=dados["produto"])
        except Produtos.DoesNotExist:
            return JsonResponse({
                "status":"erro",
                "mensagem":"Produto não encontrado."
            },status=400)
        try:
            quantidade = int(dados.get("quantidade", 0))
            if quantidade < 0:
                return JsonResponse({
                    "status": "erro",
                    "mensagem": "A quantidade não pode ser negativa."
                }, status=400)
        except Exception as e:
            return JsonResponse({
                "status":"erro",
                "mensagem": str(e)
            })
        try:
            ProdutoCores.objects.create(
                codigo=produto,
                cor=dados["cor"],
                nome=dados["nome"],
                quantidade=quantidade,
                ativo=dados["ativo"]
            )
            return JsonResponse({
                "status":"ok",
                "mensagem" : "Cor cadastrada com sucesso."
            })
        except Exception as e:
            # print(e)
            return JsonResponse({
                "status":"erro",
                "mensagem": f"Erro ao cadastrar cor: {str(e)}"
            },status=400)
    if request.method == "PUT":
        try:
            dados = json.loads(request.body)
            print(dados)
        except:
            return JsonResponse({"status":"erro","mensagem":"Corpo da requisição inválido."}, status=400)
        try:
            quantidade = int(dados.get("quantidade", 0))
            if quantidade < 0:
                return JsonResponse({
                    "status": "erro",
                    "mensagem": "A quantidade não pode ser negativa."
                }, status=400)
        except Exception as e:
            return JsonResponse({
                "status":"erro",
                "mensagem": str(e)
            })
        try:
            cor = ProdutoCores.objects.get(id_cor=dados["id"])
        except ProdutoCores.DoesNotExist:
            return JsonResponse({
                "status":"erro",
                "mensagem":"Cor não encontrada"
            })
        cor.cor = dados["cor"]
        cor.nome = dados["nome"]
        cor.ativo = dados["ativo"]
        cor.quantidade = quantidade
        cor.save()
        return JsonResponse({
            "status":"ok",
            "mensagem" : "Cor alterada com sucesso"
        })
    if request.method == "DELETE":
        try:
            id = ProdutoCores.objects.get(id_cor=id_cor)
            id.delete()
            return JsonResponse({
                'status': 'ok',
                'mensagem': 'Cor excluida com sucesso.',
                'redirect_url' : reverse('homePerfil')
            })
        except ProdutoCores.DoesNotExist:
            return JsonResponse({
                "status":"erro",
                "mensagem":"Erro ao excluir: cor não encontrada."
            },status=400)
        except Exception as e: 
            print(e)
            return JsonResponse({
            'status': 'erro',
            'redirect_url': reverse('home'),
            'mensagem': 'Erro ao deletar cor.'
            },status=400)

@ratelimit(key="user",rate="20/10m",block=True,skip_if=lambda request: request.method != "POST")
def cadastrar_imagem(request, id_imagem=None):
    if not request.user.is_staff:
            raise Http404()
    if request.method == "GET":
        raise Http404()
    if request.method == "POST":
        try:
            id_imagem = request.POST.get("id")
            codigo_produto = request.POST.get("produto")
            id_cor = request.POST.get("cor")
            arquivo = request.FILES.get("imagem")
            if not arquivo:
                return JsonResponse({
                    "status" : "erro",
                    "mensagem": "Nenhuma imagem selecionada."
                },status=500)
            produto = Produtos.objects.get(codigo=codigo_produto)
            cor = ProdutoCores.objects.get(id_cor=id_cor)
            if not id_imagem:
                ProdutoImagens.objects.create(
                    codigo=produto,
                    id_cor=cor,
                    imagem=arquivo
                )
            else:
                imagem = ProdutoImagens.objects.get(
                    id_imagem=id_imagem
                )
                imagem.id_cor = cor
                if arquivo:
                    imagem.imagem = arquivo
                imagem.save()
            return JsonResponse({
                "status":"ok",
                "mensagem":"Imagem cadastrada/atualizada com sucesso."
            })
        except Exception as e:
            return JsonResponse({
                "status":"erro",
                "mensagem":f"Erro ao cadastrar/atualizar imagem: {str(e)}"
            },status=400)
    if request.method == "DELETE":
        try:
            imagem = ProdutoImagens.objects.get(id_imagem=id_imagem)
            if imagem.imagem:
                imagem.imagem.delete(save=False)
            imagem.delete()
            return JsonResponse({
                "status":"ok",
                "mensagem": "Imagem excluida com sucesso."
            })
        except ProdutoImagens.DoesNotExist:
            return JsonResponse({
                "status":"erro",
                "mensagem":"Imagem não encontrada."
            },status=400)
        except Exception as e:
            return JsonResponse({
                "status":"erro",
                "mensagem":f"Erro ao excluir imagem: {str(e)}"
            },status=400)

@ratelimit(key="ip",rate="120/m",block=True,skip_if=lambda request: request.method != "GET")
def filtrarProduto(request,codigo=None):
    if not request.user.is_staff:
        raise Http404()
    if request.method == "GET":
        try:
            produto = Produtos.objects.get(codigo=codigo)
        except Produtos.DoesNotExist:
            return JsonResponse({
                'status' : 'erro',
                'mensagem' : 'Produto não encontrado.'
            })
        cores = ProdutoCores.objects.filter(codigo=produto)
        imagens = ProdutoImagens.objects.filter(codigo=produto)
        lista_produtos = [{
            "id": produto.id_produto,
            "codigo": produto.codigo,
            "descricao": produto.descricao,
            "valor": produto.valor,
            "is_sale" : produto.is_sale,
            "sale_value" : produto.sale_value,
            "quantidade": produto.quantidade,
            "altura": float(produto.altura),
            "largura": float(produto.largura),
            "comprimento": float(produto.comprimento),
            "volume": float(produto.volume),
            "categoria": produto.categoria,
            "ativo": produto.ativo,
            "peso": float(produto.peso),
        }]
        lista_images = [{
            "id_image": imagem.id_imagem,
            "codigo": imagem.codigo.codigo,
            "id_cor": imagem.id_cor.id_cor,
            "imagem": imagem.imagem.url,
            "cor": imagem.id_cor.cor,
        } for imagem in imagens]
        lista_cores = [{
            "id_cor": cor.id_cor,
            "produtoRef": cor.codigo.codigo,
            "cor": cor.cor,
            "nome" : cor.nome,
            "quantidade": cor.quantidade,
            "ativo": cor.ativo
        } for cor in cores]
        return JsonResponse({
            "produto": lista_produtos,
            "cores": lista_cores,
            "images": lista_images,
            'status' : 'ok',
            'mensagem' : 'Produto renderizado.'
        })


def serializar_pedido(pedido):
    return {
        "id": pedido.id,
        "nome_cliente": pedido.nome_cliente,
        "email_cliente": pedido.email_cliente,
        "telefone_cliente": pedido.telefone_cliente,
        "status": pedido.status,
        "status_display": pedido.get_status_display(),
        "subtotal": str(pedido.subtotal),
        "frete": str(pedido.frete),
        "total": str(pedido.total),
        "cep": pedido.cep,
        "endereco": pedido.endereco,
        "numero": pedido.numero,
        "complemento": pedido.complemento,
        "bairro": pedido.bairro,
        "cidade": pedido.cidade,
        "estado": pedido.estado,
        "transportadora": pedido.transportadora,
        "servico_frete": pedido.servico_frete,
        "prazo_frete": pedido.prazo_frete,
        "cotacao_frete_id": pedido.cotacao_frete_id,
        "opcao_frete_id": pedido.opcao_frete_id,
        "melhor_envio_shipment_id": pedido.melhor_envio_shipment_id,
        "melhor_envio_order_id": pedido.melhor_envio_order_id,
        "codigo_rastreio": pedido.codigo_rastreio,
        "criado_em": pedido.criado_em.strftime("%d/%m/%Y %H:%M"),
        "atualizado_em": pedido.atualizado_em.strftime("%d/%m/%Y %H:%M"),
        "mp_preference_id": pedido.mp_preference_id,
        "mp_payment_id": pedido.mp_payment_id,
        "mp_status": pedido.mp_status,
        "mp_status_detail": pedido.mp_status_detail,
        "data_pagamento": (
            pedido.data_pagamento.strftime("%d/%m/%Y %H:%M")
            if pedido.data_pagamento
            else None
        ),
        "processamento_pos_pagamento": pedido.processamento_pos_pagamento,
        "etiqueta_url": pedido.etiqueta_url,
        "etiqueta_paga": pedido.etiqueta_paga,
        "itens": [
            {
                "produto": str(item.produto.categoria.split(",")[0].strip()),
                "cor": str(item.cor.nome),
                "quantidade": item.quantidade,
                "preco_unitario": str(item.preco_unitario),
                "subtotal": str(item.subtotal),
            }
            for item in pedido.itens.all()
        ]
    }

def pesquisar_pedido(request):
    if not request.user.is_staff:
            raise Http404()
    codigo = request.GET.get("codigo", "").strip()
    if not codigo.isdigit():
        return JsonResponse({
            "status": "erro",
            "mensagem": "Código de pedido inválido."
        }, status=400)
    pedido = Pedido.objects.prefetch_related("itens__produto", "itens__cor").filter(id=int(codigo)).first()
    if not pedido:
        return JsonResponse({
            "status": "erro",
            "mensagem": "Pedido não encontrado."
        }, status=404)
    
    return JsonResponse({
        "status": "ok",
        "pedido": serializar_pedido(pedido),
        "mensagem" : "Pedido renderizado."
    })

@ratelimit(key="ip",rate="20/10m",block=True,skip_if=lambda request: request.method != "POST")
@login_required
def atualizar_status_retirada(request):
    if request.method != "POST":
        return JsonResponse({
            "status": "erro",
            "mensagem": "Método não permitido."
        }, status=405)

    if not request.user.is_staff:
            raise Http404()
    dados = json.loads(request.body)
    pedido_id = dados.get("pedido_id")
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if pedido.opcao_frete_id is not None:
        return JsonResponse({
            "status": "erro",
            "mensagem": "Este pedido não é uma retirada na loja."
        }, status=400)

    if pedido.status != "pago" and pedido.status != "preparando":
        return JsonResponse({
            "status": "erro",
            "mensagem": "Não podemos dar continuidade no pedido."
        }, status=400)
    pedido.status = dados.get("status")
    pedido.save(update_fields=["status"])
    path = reverse('homePerfil')
    link = request.build_absolute_uri(path)
    if dados.get("status") == "pronto_retirada":
        sendEmail(assunto="Pedido pronto para retirada.",
                          destinatario=pedido.email_cliente,
                          texto="O seu pedido está pronto para ser retirado. Venha até a cerâmica buscar.",
                          texto_botao="Ver pedido",
                          link_botao=link,
                          username=pedido.nome_cliente)
    return JsonResponse({
        "status": "ok",
        "mensagem": f"Status atualizado para: {dados.get('status')}"
    })