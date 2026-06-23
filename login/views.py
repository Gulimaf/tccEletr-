from django.shortcuts import render
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404,redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from .models import Perfil
from core.models import Produtos, ProdutoCores, ProdutoImagens
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.safestring import mark_safe
from login.utils.token_generator import token_generator
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
import json
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
    except Exception as e:
        print("ERRO AO ENVIAR EMAIL:", e)
        
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
        user = User.objects.create_user(username=nome, email=email, password=password)
        userPerfil = Perfil.objects.create(
            user=user,
            telefone=telefone,
        )
        user.is_active = False
        user.save()
        token = token_generator.make_token(user)
        path = reverse('confirmar-email', args=[user.pk, token])
        link = request.build_absolute_uri(path)
        sendEmail(assunto="Confirme seu cadastro",
                  destinatario=email,
                  texto="Clique no botão abaixo para confirmar seu cadastro",
                  texto_botao="Confirmar email",
                  link_botao=link,
                  username=user.username)
        messages.success(request,('verifique seu email para ativar sua conta'))
        return redirect('register')
def confirmarEmail(request,user_id,token):
    if request.method == "GET":
        print("DADOS RECEBIDOS:",user_id,token)
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            messages.error(request,'Usuário não encontrado, tente fazer o cadastro novamente')
            return render(request, 'cadastro.html')
        if not token_generator.check_token(user, token):
            messages.error(request,'Token inexistente mande o email de novo')
            return redirect('reenviar-confirmacao')
        else:
            user.is_active = True
            user.save()
            return render(request, 'emailConfirmado.html')
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
            return redirect('precisaConfirmar')
        login(request,user)
        return redirect('homePerfil')

def reenviarConfirmacao(request):
    if request.method == "GET":
        return render(request,'precisaConfirmar.html')
    if request.method == "POST":
        email = request.session.get('email_confirmacao')
        user = User.objects.filter(email=email).first()
        if not email:
            messages.error(request, 'Sem email válido')
            return render(request,'precisaConfirmar.html')
        if not user:
            messages.error(request, 'Usuário não encontrado tente fazer o cadastro novamente')
            return render(request,'cadastro.html')
        token = token_generator.make_token(user)
        link = request.build_absolute_uri(
            f"/perfil/confirmar-email/{user.pk}/{token}/"
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
    

@login_required(login_url="/login/")
def loadPerfil(request):
    if not request.user.is_active:
        return redirect('precisaConfirmar')
    if request.user.is_staff:
        produtos = Produtos.objects.all()
        cores = ProdutoCores.objects.all()
        images = ProdutoImagens.objects.all()
        lista_images = [{
            "id_image" : i.id_imagem,
            "codigo" : i.codigo.codigo,
            "id_cor" : i.id_cor.id_cor,
            "imagem" : i.imagem.url,

        }
        for i in images
        ]
        lista_cores = [{
            "id_cor" : c.id_cor,
            "produtoRef":c.codigo.codigo,
            "cor":c.cor
        }
        for c in cores
        ]
        lista_produtos = [{
            "id" : p.id_produto,
            "codigo" : p.codigo,
            "descricao" : p.descricao,
            "valor" : p.valor,
            "quantidade" : float(p.quantidade),
            "altura": float(p.altura),
            "largura" : float(p.largura),
            "comprimento" : float(p.comprimento),
            "volume" : float(p.volume),
            "categoria" : p.categoria,
            "ativo" : p.ativo,
            "peso" : float(p.peso)
        }
            for p in produtos
        ]
        return render(request, 'perfilStaff.html', {
            'produtos_json' : json.dumps(lista_produtos),
            'cores_json':json.dumps(lista_cores),
            'images_json':json.dumps(lista_images)
            })
    return render(request, 'perfil.html')

def logoutF(request):
    if request.method == "POST":
        logout(request)
        return redirect('home')
    if request.method == "GET":
        return redirect('home')
    
def redefinirSenha(request):
    if request.method == "GET":
        return render(request, 'email.html')
    if request.method == "POST":
        email = request.POST.get('email')
        print(email)
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
    
def resetPassword(request,user_id, token):
    if request.method == 'GET':
        return render(request,  'forgotPass.html')
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error('Usuário inexistente, tente fazer o processo novamente')
        return render(request, 'forgotPass.html')
    if not token_generator.check_token(user,token):
        messages.error('token inválido envie o email novamente')
        return render(request, 'forgotPass.html')
    novaSenha = request.POST.get('novaSenha')
    repeatedNovaSenha = request.POST.get('repeatedNovaSenha')
    if (novaSenha == repeatedNovaSenha):
        user.set_password(novaSenha)
        user.save()
        print(user)
    login_url = reverse('login')
    messages.success(request,mark_safe(
        f'Senha alterada com sucesso <a href="{login_url}">Fazer login</a>'
    ))
    return render(request, 'forgotPass.html')

def cadProduto(request,id_produto=None):
    print("METODO")
    print(request.method)
    if request.method == "GET":
        return HttpResponse('a')
    if request.method == "POST":
        codigo = request.POST.get('codigo')
        descricao = request.POST.get('descricao')
        valor = request.POST.get('valor')
        quantidade = request.POST.get('quantidade')
        altura = request.POST.get('altura')
        largura = request.POST.get('largura')
        comprimento = request.POST.get('comprimento')
        volume = request.POST.get('volume')
        categoria = request.POST.get('categoria')
        ativo = request.POST.get('ativo')
        peso = request.POST.get('peso')
        if ativo == 'S':
            ativo = True
        else:
            ativo = False
        if all([codigo,descricao,valor,quantidade,categoria,ativo]):
            Produtos.objects.create(
                descricao=descricao,
                valor=valor,
                codigo=codigo,
                quantidade=quantidade,
                categoria=categoria.split(','),
                ativo=ativo,
                altura=altura,
                largura=largura,
                comprimento=comprimento,
                volume=volume,
                peso=peso
            )
        print(categoria)
        return redirect('homePerfil')
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({'erro':'Corpo da requisição inválido'}, status=400)
        id = data.get('id')
        codigo = data.get('codigo')
        valor = data.get('valor')
        quantidade = data.get('quantidade')
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
                codigo=codigo,
                quantidade=quantidade,
                categoria=categoria.split(','),
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
        except: 
            return JsonResponse({
            'status': 'erro',
            'redirect_url': reverse('home') 
            })
    if request.method == 'DELETE':
        try:
            id = get_object_or_404(Produtos, id_produto=id_produto)
            id.delete()
            print("sucesso")
            return JsonResponse({
                'status': 'ok',
                'redirect_url' : reverse('homePerfil')
            })
        except: 
            return JsonResponse({
            'status': 'erro',
            'redirect_url': reverse('home') 
            })

    

def cadastrar_cor(request):
    produtos = Produtos.objects.all()
    cores = ProdutoCores.objects.all()
    if request.method == "POST":
        codigo = request.POST.get("produto")
        cor = request.POST.get("cor")
        produto = Produtos.objects.get(codigo=codigo)
        ProdutoCores.objects.create(
            codigo=produto,
            cor=cor
        )
        return redirect("homePerfil")
    return render(request, "perfilStaff.html", {
        "produtos": produtos,
        "cores":cores,
    })  

def cadastrar_imagem(request):
    if request.method == "GET":
        return redirect('home')
    if request.method == "POST":
        try:
            codigoProduto = request.POST.get('produto')
            corProduto = request.POST.get('cor')
            imagemProduto = request.FILES.get('imagem')
            produto = Produtos.objects.get(codigo=codigoProduto)
            print(corProduto)
            cor = ProdutoCores.objects.get(cor=corProduto,codigo=produto)
            print("Produto:", produto)
            print("Cor:", cor)
            print("Imagem:", imagemProduto)
            imagem = ProdutoImagens.objects.create(
                codigo=produto,
                id_cor=cor,
                imagem=imagemProduto
            )
        except Produtos.DoesNotExist:
            print("Produto não encontrado")

        except ProdutoCores.DoesNotExist:
            print("Cor não encontrada para este produto")
        return redirect('homePerfil')
