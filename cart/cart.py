from core.models import Produtos, ProdutoImagens, ProdutoCores
import hashlib
import json
class Cart():
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('session_key')
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}
        self.cart = cart

    def add(self,produto, id_cor, quantidade=1):
        produto_id = str(produto.id_produto)
        id_cor = str(id_cor)
        item_id = f"{produto_id}-{id_cor}"  
        try: 
            cor = ProdutoCores.objects.get( id_cor=id_cor, codigo=produto ) 
        except ProdutoCores.DoesNotExist: 
            return False, "Cor não encontrada."
        estoque = cor.quantidade
        if estoque <= 0: 
            return False, "Essa cor está sem estoque."
        quantidade = int(quantidade) 
        if quantidade < 1: 
            quantidade = 1
        if item_id in self.cart: 
            quantidade_atual = self.cart[item_id]['quantidade'] 
            nova_quantidade = quantidade_atual + quantidade  
            nova_quantidade = min( nova_quantidade, estoque ) 
            self.cart[item_id]['quantidade'] = nova_quantidade 
            self.session.modified = True    
        else:  
            quantidade = min( quantidade, estoque ) 
            self.cart[item_id] = { 
                'produto_id': produto_id, 
                'id_cor': id_cor, 
                'quantidade': quantidade 
                } 
            self.session.modified = True
            return True, "Produto adicionado ao carrinho."

    def __len__(self):
        return len(self.cart)
    def get_produtos(self): 
        if not self.cart: 
            return [] 
        produtos_lista = [] 
        for item_id, item in self.cart.items(): 
            produto_id = item['produto_id'] 
            id_cor = item['id_cor'] 
            try: 
                produto = Produtos.objects.get( id_produto=produto_id ) 
                cor = ProdutoCores.objects.get( id_cor=id_cor, codigo=produto ) 
            except ( Produtos.DoesNotExist, ProdutoCores.DoesNotExist ): 
                continue 
            if produto.is_sale:
                preco = float(produto.sale_value)
            else:
                preco = float(produto.valor)
            categorias = [ categoria.strip() for categoria in produto.categoria.split(",") if categoria.strip() ] 
            nome = ( categorias[0] if categorias else "Produto sem nome" ) 
            imagem = ProdutoImagens.objects.filter( codigo=produto, id_cor=cor ).first()  
            quantidade = int(item['quantidade'])
            subtotal = preco * quantidade
            produtos_lista.append({
                'produto': produto,
                'cor': cor,
                'imagem': imagem,
                'nome': nome,
                'quantidade': quantidade,
                'max_quantidade': cor.quantidade,
                'preco': preco,
                'subtotal': subtotal,
                'item_id': item_id
            })
        return produtos_lista
    def update_quantity(self, produto_id, id_cor, quantidade): 
        produto_id = str(produto_id) 
        id_cor = str(id_cor) 
        item_id = f"{produto_id}-{id_cor}" 
        if item_id not in self.cart: 
            return False, "Item não está no carrinho." 
        try: 
            quantidade = int(quantidade) 
        except (TypeError, ValueError): 
            return False, "Quantidade inválida." 
        if quantidade < 1: 
            quantidade = 1 
        try: 
            cor = ProdutoCores.objects.get( id_cor=id_cor, codigo_id=produto_id ) 
        except ProdutoCores.DoesNotExist: 
            return False, "Cor não encontrada." 
        estoque = cor.quantidade 
        if estoque <= 0: 
            return False, "Essa cor está sem estoque."  
        quantidade = min( quantidade, estoque ) 
        self.cart[item_id]['quantidade'] = quantidade 
        self.session.modified = True 
        return True, quantidade
    def remove(self, produto_id, id_cor): 
        produto_id = str(produto_id) 
        id_cor = str(id_cor) 
        item_id = f"{produto_id}-{id_cor}" 
        if item_id in self.cart: 
            del self.cart[item_id] 
            self.session.modified = True 
            return True 
        return False
    def get_cart_hash(self):
        itens = []
        for item_id, item in self.cart.items():
            itens.append({
                "produto_id": str(item["produto_id"]),
                "id_cor": str(item["id_cor"]),
                "quantidade": int(item["quantidade"])
            })
        itens.sort(
            key=lambda x: (
                x["produto_id"],
                x["id_cor"]
            )
        )
        conteudo = json.dumps(
            itens,
            sort_keys=True
        )
        return hashlib.sha256(
            conteudo.encode()
        ).hexdigest()
    def get_produtos_frete(self):
        produtos = []
        for item_id, item in self.cart.items():
            try:
                produto = Produtos.objects.get(id_produto=item["produto_id"])
                cor = ProdutoCores.objects.get(id_cor=item["id_cor"],codigo=produto)
            except(Produtos.DoesNotExist,ProdutoCores.DoesNotExist):
                continue
            preco_atual = float(produto.sale_value) if produto.is_sale else float(produto.valor)
            quantidade = int(item["quantidade"])
            produtos.append({
                "id": str(produto.id_produto),
                "width": float(produto.largura),
                "height": float(produto.altura),
                "length": float(produto.comprimento),
                "weight": float(produto.peso),
                "insurance_value": preco_atual * quantidade,
                "quantity": quantidade
            })
        return produtos