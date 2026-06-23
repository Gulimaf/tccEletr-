function getCsrfToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      const c = cookie.trim();
      if (c.startsWith("csrftoken=")) {
        return c.substring("csrftoken=".length, c.length);
      }
    }
    return "";
}

// Nav: fundo ao rolar
const nav = document.getElementById('nav');
window.addEventListener('scroll', function () {
  nav.classList.toggle('scrolled', window.scrollY > 40);
}, { passive: true });
 
// Menu mobile
const burger = document.getElementById('burger');
const navLinks = document.getElementById('navLinks');
if(burger){
  burger.addEventListener('click', function () {
    navLinks.classList.toggle('on');
    burger.classList.toggle('active'); // <- animação do X
  });
}
if(navLinks){
  navLinks.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', function () {
      navLinks.classList.remove('on');
      burger.classList.remove('active'); // <- fecha o X ao clicar num link
    });
  });
}
 
// Animação reveal ao rolar
const reveals = document.querySelectorAll('.reveal');
 
const observer = new IntersectionObserver(function (entries) {
  entries.forEach(function (entry, i) {
    if (entry.isIntersecting) {
      setTimeout(function () {
        entry.target.classList.add('visible');
      }, i * 80);
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });
 
reveals.forEach(function (el) {
  observer.observe(el);
});
const telefone = document.querySelector('.telInput');
if(telefone){
  telefone.addEventListener('input', () => {
  telefone.value = telefone.value
    .replace(/\D/g, '')
    .slice(0, 11);
});
}
const forms = document.querySelectorAll('.formLogin');
forms.forEach(form => {
  const usernameInput = form.querySelector('.usernameInput');
  const passInput = form.querySelector('.passInput');
  const emailInput = form.querySelector('.emailInput');
  const sendFormbtn = form.querySelector('.sendForm');
  const listaObrigatoria = document.querySelector('.listaObrig');
  if (listaObrigatoria){
      const itens = listaObrigatoria.querySelectorAll('.itemLista');
      itens.forEach(item => {
        item.style.color = 'red';
        if (passInput){
        passInput.addEventListener('keyup',function() {
          const senhaValue = passInput.value;
          if (item.classList.contains('caracter')){
            if (senhaValue.trim().length >= 8) item.style.color = 'green', item.style.backgroundColor = '#F0FFF0', item.style.border = '1px solid green';
            else item.style.color = 'red', item.style.backgroundColor = '#ffebee', item.style.border = '1px solid #e53935';
          };
          if (item.classList.contains('umNum')){
            if (/\d/.test(senhaValue)) item.style.color = item.style.color = 'green', item.style.backgroundColor = '#F0FFF0', item.style.border = '1px solid green';
            else item.style.color = 'red', item.style.backgroundColor = '#ffebee', item.style.border = '1px solid #e53935';
          };
          if (item.classList.contains('umL')){
            if (/[A-Z]/.test(senhaValue)) item.style.color = 'green', item.style.backgroundColor = '#F0FFF0', item.style.border = '1px solid green';
            else item.style.color = 'red', item.style.backgroundColor = '#ffebee', item.style.border = '1px solid #e53935';
          };
          if (item.classList.contains('especial')){
            if (/[^A-Za-z0-9]/.test(senhaValue)) item.style.color = 'green', item.style.backgroundColor = '#F0FFF0', item.style.border = '1px solid green';
            else item.style.color = 'red', item.style.backgroundColor = '#ffebee', item.style.border = '1px solid #e53935';
          };
        })
      }
      });
  };
  form.addEventListener('submit', e =>{
    let erroSenha = false;
    let erro = false;
    if (usernameInput && usernameInput.value.trim() === '') erro = true;
    if (passInput && passInput.value.trim() === '') erro = true;
    if (emailInput && emailInput.value.trim() === '') erro = true;
    if (passInput){
      const senhaValue = passInput.value;
      const regrasSenhaInvalidas = [
        senhaValue.length < 8,
        !/\d/.test(senhaValue),
        !/[A-Z]/.test(senhaValue),
        !/[^A-Za-z0-9]/.test(senhaValue)
      ];
      if (regrasSenhaInvalidas.some(r => r)) erroSenha = true;
  }
    if (erroSenha){
      verificarErro('Verifique sua senha',form,e,sendFormbtn)
      return;
    }
    if (erro){
      verificarErro('Todos os campos devem ser preenchidos',form,e,sendFormbtn)
      return;
    }
    
  })
});
function verificarErro(msg,form,e,sendFormbtn){
  e.preventDefault();
  const errorExists = form.querySelector('.errorForm');
  if (errorExists) errorExists.remove();
  const span = document.createElement('span');
  span.classList.add('errorForm');
  span.innerHTML = `<i data-lucide="circle-x" style="color:red;width:20px;height:20px;"></i> ${msg}`;
  sendFormbtn.before(span);
  lucide.createIcons();
}

async function sendConfirm() {
    try{
      const csrfToken = getCsrfToken();
      const headers = {
        'Content-Type' : 'application/json',
        'X-CSRFToken' : csrfToken
      }
      const init = {
        method:'POST',
        headers:headers,
      }
      const response = await fetch('/reenviar-confirmacao/',init);
    }
    catch(e){
      console.log(e);
    }
}
const btnSendConfirm = document.querySelector('.btnSendConfirm');
if(btnSendConfirm){
  btnSendConfirm.addEventListener('click', ()=>{
    sendConfirm();
  })
}

async function logout(){
  try{
      const csrfToken = getCsrfToken();
      const headers = {
        'Content-Type' : 'application/json',
        'X-CSRFToken' : csrfToken
      }
      const init = {
        method:'POST',
        headers:headers,
      }
      const response = await fetch('/logout/',init);
      window.location.href = '/';
    }
    catch(e){
      console.log(e);
    }
}
const logoutBtn = document.querySelector('.logoutBtn');
if(logoutBtn){
  logoutBtn.addEventListener('click', ()=>{
    logout();
  })
}
document.querySelectorAll('.pass-group').forEach(group => {
  const eye = group.querySelector('.eye');
  const input = group.querySelector('.passInput');
  if (!eye || !input) return;
  let open = false;
  eye.addEventListener('click', () => {
    open = !open;
    input.type = open ? 'text' : 'password';
    eye.innerHTML = `
      <i data-lucide="${open ? 'eye' : 'eye-off'}"></i>`;
    lucide.createIcons();
  });
});

let produtos;
let cores;
let images;
function getJson(){
    try{
        produtos = JSON.parse(document.getElementById("jsonProdutos").textContent);
        cores = JSON.parse(document.getElementById("jsonCores").textContent);
        images = JSON.parse(document.getElementById("jsonImages").textContent);
        console.log(cores);
    } catch(e){
        console.log(e);
        return;
    }
    let card;
    const cardsProduto = document.querySelector('.cardsProduto');
    for(let i = 0; i < produtos.length;i++){
        card = document.createElement('div');
        card.classList.add('cardProduto');
        const containerImagens = document.createElement('div');
        containerImagens.classList.add('containerImagens');
        for(let img of images){
          if (img.codigo !== produtos[i].codigo) {
              continue;
          }
          const image = document.createElement('img');
          image.src = img.imagem;
          image.alt = produtos[i].descricao;
          image.style.width = '80px';
          image.style.height = '100px';
          image.style.objectFit = 'cover';
          image.style.borderRadius = '5px';
          image.style.border = '1px solid #ccc';
          containerImagens.appendChild(image);
        }
        card.appendChild(containerImagens);
        for(let k in produtos[i]){
            const p = document.createElement('p');
            p.classList.add(`${k}`)
            p.innerHTML = `${k} : ${produtos[i][k]}`;
            p.dataset.id = `${produtos[i][k]}`
            card.appendChild(p);
        };
        const deleteButton = document.createElement("button");
        deleteButton.innerHTML = 'Deletar'
        deleteButton.classList.add('btnDelete')
        const edtButton = document.createElement("button");
        edtButton.innerHTML = 'Editar';
        edtButton.classList.add('edtButton');
        card.appendChild(edtButton);
        card.appendChild(deleteButton);
        cardsProduto.appendChild(card);
        let splitCard = document.createElement('p');
        splitCard.innerHTML = 'Cores';
        splitCard.classList.add('splitText');
        card.appendChild(splitCard)
        for(let a =0; a < cores.length;a++){ 
            if(cores[a].produtoRef !== produtos[i].codigo){
              continue;
            }
            const div = document.createElement('div');
            div.classList.add('cor');
            div.classList.add(`${cores[a].cor}`)
            div.style.width = '30px';
            div.style.height = '30px';
            div.style.borderRadius = '50%';
            div.style.backgroundColor = cores[a].cor.startsWith('#') ? `${cores[a].cor}` : `#${cores[a].cor}`;
            card.appendChild(div);
        }
      }
    return produtos;
}
getJson();
function updateForm(id,codigo,valor,quantidade,altura,largura,comprimento,volume,categoria,ativo,peso,descricao){
    const form = document.querySelector('.edtForm');
    const elements = form.querySelectorAll('.edtForm input:not([name="csrfmiddlewaretoken"]), .edtForm textarea');
    const lista = [id,codigo,valor,quantidade,altura,largura,comprimento,volume,categoria,ativo,peso,descricao];
    for(let i = 0; i < elements.length -1; i++){
        elements[i].value = String(lista[i])
        .replace('[', '')
        .replace(']', '')
        .replaceAll("'", '');
    }
}

document.querySelectorAll('.cardProduto').forEach(function(card){
    const cardEl = card;
    const edtBtn = cardEl.querySelector('.edtButton');
    let id;
    let codigo;
    let valor;
    let quantidade;
    let altura;
    let largura;
    let comprimento;
    let volume;
    let categoria;
    let ativo;
    let peso;
    let descricao;
    try{
        id = cardEl.querySelector('.id').dataset.id
        codigo = cardEl.querySelector('.codigo').dataset.id;
        valor = cardEl.querySelector('.valor').dataset.id;
        quantidade = cardEl.querySelector('.quantidade').dataset.id;
        altura = cardEl.querySelector('.altura').dataset.id;
        largura = cardEl.querySelector('.largura').dataset.id;
        comprimento = cardEl.querySelector('.comprimento').dataset.id;
        volume = cardEl.querySelector('.volume').dataset.id;
        categoria = cardEl.querySelector('.categoria').dataset.id;
        ativo = cardEl.querySelector('.ativo').dataset.id;
        peso = cardEl.querySelector('.peso').dataset.id;
        descricao = cardEl.querySelector('.descricao').dataset.id;
    } catch(e){
        console.log(e);
        return;
    }
    edtBtn.addEventListener('click', function(){
        updateForm(id,codigo,valor,quantidade,altura,largura,comprimento,volume,categoria,ativo, peso,descricao);
    })
});

async function editProduct(id,codigo,descricao,valor,quantidade,altura,largura,comprimento,volume,categoria,ativo, peso){
    try{
        const csrfToken = getCsrfToken();
        const headers = {
        'Content-Type' : 'application/json',
        'X-CSRFToken' : csrfToken
        }
        const init = {
        method:'PUT',
        headers:headers,    
        body: JSON.stringify({
            id:id,
            codigo:codigo,
            valor:valor,
            quantidade:quantidade,
            altura:altura,
            largura:largura,
            comprimento:comprimento,
            volume:volume,
            categoria:categoria,
            ativo:ativo,
            peso:peso,
            descricao:descricao

        })
        }
        const response = await fetch(`/cadastrar-produto/`, init);
        const data = await response.json();
        if (data.status === 'ok'){
            if (data.redirect_url) {
                window.location.href = data.redirect_url;
            }
        }
        if (data.status === 'erro'){
            console.log('Erro trazido pelo backend, verifique o terminal');
        }
    } catch(e){
        console.log(e);
    }
}
const edtBtn = document.querySelector('.edtForm .btnSendEdt');
if(edtBtn){
    edtBtn.addEventListener('click',function(e){
        const form = document.querySelector('.edtForm');
        const id = form.querySelector('.id').value;
        const codigo = form.querySelector('.codigo').value;
        const valor = form.querySelector('.valor').value;
        const quantidade = form.querySelector('.quantidade').value;
        const altura = form.querySelector('.altura').value;
        const largura = form.querySelector('.largura').value;
        const comprimento = form.querySelector('.comprimento').value;
        const volume = form.querySelector('.volume').value;
        const categoria = form.querySelector('.categoria').value;
        const ativo = form.querySelector('.ativo').value;
        const peso = form.querySelector('.peso').value;
        const descricao = form.querySelector('.descricao').value;
        e.preventDefault();
        console.log('botão clicado');
        editProduct(id,codigo,descricao,valor,quantidade,altura,largura,comprimento,volume,categoria,ativo, peso);
    })
}
async function deletarProduto(id){
    try{
        const csrfToken = getCsrfToken();
        const headers = {
        'Content-Type' : 'application/json',
        'X-CSRFToken' : csrfToken
        }
        const init = {
        method:'DELETE',
        headers:headers,
        }
        const response = await fetch(`/cadastrar-produto/${id}/`, init);
        const data = await response.json();
        if (data.status === 'ok'){
            if (data.redirect_url) {
                window.location.href = data.redirect_url;
            }
        }
        if (data.status === 'erro'){
            console.log('Erro trazido pelo backend, verifique o terminal');
        }
    } catch(e){
        console.log(e);
    }
}
document.querySelectorAll('.cardProduto').forEach(function(card){
    const cardEl = card;
    const btnDelete = cardEl.querySelector('.btnDelete');
    try{
        const id = cardEl.querySelector('.id').dataset.id;
        btnDelete.addEventListener('click', function(){
        deletarProduto(id);
    })
    }catch(e){
        return;
    }
})
function preencherSelects(selects, produtos) {
  selects.forEach(select => {
    preencherSelect(select, produtos);
  });
}
function preencherSelect(select, produtos) {
  for (let i = 0; i < produtos.length; i++) {
    const option = document.createElement('option');
    option.value = produtos[i].codigo;
    option.innerText = "Código: " + produtos[i].codigo;
    select.appendChild(option);
  }
}

function preencherCores(select, cores) {
  const fragment = document.createDocumentFragment();
  cores.forEach(cor => {
    const option = document.createElement('option');
    option.value = cor.cor;
    option.innerHTML = `&#9679; ${cor.cor}`;
    option.style.color = cor.cor.startsWith('#') ? `${cor.cor}` : `#${cor.cor}` 
    fragment.appendChild(option);
  });
  select.appendChild(fragment);
}

document.addEventListener("DOMContentLoaded", () => {
  const selectsProduto = document.querySelectorAll(".selectProduct");
  const selectsCor = document.querySelectorAll(".selectColor");
  selectsCor.forEach(sc => sc.disabled = true);
  selectsProduto.forEach(select => {
    preencherSelect(select, produtos);
    select.addEventListener("change", (e) => {
      const produtoId = e.target.value;
      if (!produtoId) {
        selectsCor.forEach(sc => {
          sc.innerHTML = `<option value="">Selecione uma cor</option>`;
          sc.disabled = true;
        });
        return;
      }
      const coresFiltradas = cores.filter(c => c.produtoRef == produtoId);
      selectsCor.forEach(sc => {
        sc.disabled = false;
        preencherCores(sc, coresFiltradas);
      });
    });
  });
  getJsonDetalhes();
});
const inputImage = document.querySelector('.inputImage');
const preview = document.querySelector('.previewImage');
if(inputImage && preview){
  inputImage.addEventListener('change',e=>{
    const file = e.target.files[0];
    if(!file) return;
    const url = URL.createObjectURL(file)
    preview.src = url;
    preview.style.display = 'block';
    preview.onload = () => {
      URL.revokeObjectURL(preview.src);
    };
  })
}
let imagesPaginaProdutos;
let produtosPaginaProdutos;
function getJsonPaginaProdutos(){
  try {
    produtosPaginaProdutos = JSON.parse(document.getElementById("jsonProdutosPaginaProdutos").textContent);
    imagensPaginaProdutos = JSON.parse(document.getElementById("jsonImagesPaginaProdutos").textContent);
  } catch (e) {
    console.log(e);
    return;
  }
  const container = document.querySelector(".produtosContainer");
  produtosPaginaProdutos.forEach(produto => {
    const card = document.createElement("div");
    card.classList.add("obra-card");
    const imgObj = imagensPaginaProdutos.find(img => img.codigo === produto.codigo);
    const img = document.createElement("img");
    img.classList.add("obra");
    img.src = imgObj ? imgObj.imagem : "/static/img/placeholder.jpg";
    img.alt = produto.codigo;
    const link = document.createElement("a");
    link.classList.add("verMaisObra");
    link.textContent = "Ver mais";
    link.href = `/produtos/${produto.codigo}/`;
    card.appendChild(img);
    card.appendChild(link);
    container.appendChild(card);
  });
}
getJsonPaginaProdutos();
let produtoPaginaDetalhes;
let coresPaginaDetalhes;
let imagensPaginaDetalhes;
function getJsonDetalhes() {
  try {
    produtoPaginaDetalhes = JSON.parse(document.getElementById("jsonProdutos").textContent);
    coresPaginaDetalhes = JSON.parse(document.getElementById("jsonCores").textContent);
    imagensPaginaDetalhes = JSON.parse(document.getElementById("jsonImages").textContent);
  } catch (e) {
    console.log("Erro ao ler JSON:", e);
    return;
  }
  renderProduto();
  renderCores();
  renderImagemInicial();
}
function renderProduto() {
  let nome = "Indefinido";
  if (produtoPaginaDetalhes.categoria) {
    nome = produtoPaginaDetalhes.categoria.split(",")[0].trim();
  }
  document.querySelector(".nomeProduto").textContent = nome;
  document.querySelector(".descricaoProduto").textContent =produtoPaginaDetalhes.descricao || "Sem descrição";
  document.querySelector(".valorProduto").textContent =`R$ ${produtoPaginaDetalhes.valor}`;
  // document.querySelector(".proporcaoProduto").textContent =`${produtoPaginaDetalhes.altura} x ${produtoPaginaDetalhes.largura} x ${produtoPaginaDetalhes.comprimento}`;
  if (produtoPaginaDetalhes.volume) {
    const volumeEl = document.querySelector(".volumeContainer");
    if (volumeEl) {
      volumeEl.style.display = "block";
      document.querySelector(".volumeProduto").textContent = produtoPaginaDetalhes.volume;
    }
  }
}
function renderCores() {
  const container = document.querySelector(".coresContainer");
  container.innerHTML = "";
  coresPaginaDetalhes.forEach(cor => {
    const btn = document.createElement("div");
    btn.style.width = "25px";
    btn.style.height = "25px";
    btn.style.borderRadius = "50%";
    btn.style.margin = "5px";
    btn.style.display = "inline-block";
    btn.style.cursor = "pointer";
    btn.style.backgroundColor = cor.cor.startsWith("#") ? cor.cor: `#${cor.cor}`;
    btn.addEventListener("click", () => {
      trocarImagem(cor.id_cor);
    });
    container.appendChild(btn);
  });
}
function renderImagemInicial() {
  if (coresPaginaDetalhes.length > 0) {
    trocarImagem(coresPaginaDetalhes[0].id_cor);
  }
}
function trocarImagem(idCor) {
  const imgObj = imagensPaginaDetalhes.find(img => img.id_cor === idCor);
  const imgEl = document.querySelector(".produtoImagem");
  imgEl.src = imgObj
    ? imgObj.imagem
    : "/static/img/placeholder.jpg";
  imgEl.alt = produtoPaginaDetalhes.codigo;
}
const formEncomenda = document.querySelector('.cancelar');
if(formEncomenda){
  formEncomenda.addEventListener('submit', e=>{
    alert('Esse formulário ainda não foi programado.');
    e.preventDefault();
  })
}