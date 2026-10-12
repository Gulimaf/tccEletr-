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
const burger = document.getElementById('burger');
const navLinks = document.getElementById('navLinks');
if(burger){
  burger.addEventListener('click', function () {
    navLinks.classList.toggle('on');
    burger.classList.toggle('active');
  });
}
if(navLinks){
  navLinks.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', function () {
      navLinks.classList.remove('on');
      burger.classList.remove('active');
    });
  });
}
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
function mostrarLoading() {
    document.getElementById('loading').classList.add('ativo');
}

function esconderLoading() {
    document.getElementById('loading').classList.remove('ativo');
}
const forms = document.querySelectorAll('.formLogin');
document.addEventListener("DOMContentLoaded", () => {
    const forms = document.querySelectorAll(".formLogin");
    const telefones = document.querySelectorAll('input[type="tel"]');

    const regrasSenha = [
        {
            seletor: ".caracter",
            validar: senha => senha.length >= 8
        },
        {
            seletor: ".umNum",
            validar: senha => /\d/.test(senha)
        },
        {
            seletor: ".umL",
            validar: senha => /[A-Z]/.test(senha)
        },
        {
            seletor: ".especial",
            validar: senha => /[^A-Za-z0-9]/.test(senha)
        }
    ];

    function mostrarLoading() {
        document.getElementById("loading")?.classList.add("ativo");
    }

    function esconderLoading() {
        document.getElementById("loading")?.classList.remove("ativo");
    }

    function verificarErro(msg, form, event, botao) {
        event.preventDefault();

        const erroExistente = form.querySelector(".errorForm");
        if (erroExistente) erroExistente.remove();

        const span = document.createElement("span");
        span.classList.add("errorForm");

        span.innerHTML = `
            <i data-lucide="circle-x"
               style="color:red;width:20px;height:20px;">
            </i>
            ${msg}
        `;

        botao?.before(span);
        lucide.createIcons();
    }

    function atualizarRegrasSenha(form) {
        const senhaInput = form.querySelector(".passInput");
        const lista = form.querySelector(".listaObrig");

        if (!senhaInput || !lista) return;

        const senha = senhaInput.value;

        regrasSenha.forEach(regra => {
            const itens = lista.querySelectorAll(regra.seletor);
            const valido = regra.validar(senha);

            itens.forEach(item => {
                item.style.color = valido ? "green" : "red";
                item.style.backgroundColor = valido
                    ? "#F0FFF0"
                    : "#ffebee";
                item.style.border = valido
                    ? "1px solid green"
                    : "1px solid #e53935";
            });
        });
    }

    function validarFormulario(form, event) {
        const username = form.querySelector(".usernameInput");
        const senhaInput = form.querySelector(".passInput");
        const email = form.querySelector(".emailInput");

        const botao = form.querySelector(
            'input[type="submit"], button[type="submit"], .sendForm'
        );

        const campos = [username, senhaInput, email].filter(Boolean);

        const campoVazio = campos.some(
            campo => campo.value.trim() === ""
        );

        if (campoVazio) {
            esconderLoading();
            verificarErro(
                "Todos os campos devem ser preenchidos",
                form,
                event,
                botao
            );
            return false;
        }

        if (senhaInput) {
            const senha = senhaInput.value;

            const senhaInvalida = regrasSenha.some(
                regra => !regra.validar(senha)
            );

            if (senhaInvalida) {
                esconderLoading();
                verificarErro(
                    "Verifique sua senha",
                    form,
                    event,
                    botao
                );
                return false;
            }
        }

        return true;
    }

    forms.forEach(form => {
        const senhaInput = form.querySelector(".passInput");

        const botao = form.querySelector(
            'input[type="submit"], button[type="submit"], .sendForm'
        );

        if (senhaInput) {
            senhaInput.addEventListener("input", () => {
                atualizarRegrasSenha(form);
            });
        }

        form.addEventListener("submit", event => {
            if (!validarFormulario(form, event)) return;

            mostrarLoading();

            if (botao) {
                botao.disabled = true;
                botao.style.opacity = "0.6";
                botao.style.cursor = "not-allowed";
            }
        });
    });

    telefones.forEach(input => {
        input.addEventListener("input", event => {
            let telefone = event.target.value
                .replace(/\D/g, "")
                .substring(0, 11);

            if (telefone.length <= 2) {
                event.target.value = `(${telefone}`;
            } else if (telefone.length <= 6) {
                event.target.value =
                    `(${telefone.substring(0, 2)}) ` +
                    telefone.substring(2);
            } else if (telefone.length <= 10) {
                event.target.value =
                    `(${telefone.substring(0, 2)}) ` +
                    `${telefone.substring(2, 6)}-` +
                    telefone.substring(6);
            } else {
                event.target.value =
                    `(${telefone.substring(0, 2)}) ` +
                    `${telefone.substring(2, 7)}-` +
                    telefone.substring(7);
            }
        });
    });

    const mensagemSalva = sessionStorage.getItem("mensagem_reload");

    if (mensagemSalva) {
        try {
            const mensagem = JSON.parse(mensagemSalva);

            sessionStorage.removeItem("mensagem_reload");
            mostrarMensagem(mensagem);
        } catch (error) {
            console.error("Erro ao ler mensagem:", error);
            sessionStorage.removeItem("mensagem_reload");
        }
    }
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
function mostrarMensagem2(resposta) {
    const container = document.querySelector(".mensagens");
    if (!container) {
        console.error("Container .mensagens não encontrado.");
        return;
    }
    container.innerHTML = "";
    const sucesso = resposta.status === "ok";
    const mensagem = document.createElement("div");
    mensagem.classList.add("errorForm",sucesso ? "success" : "error");
    mensagem.innerHTML = `
        <i data-lucide="${sucesso ? "circle-check" : "circle-x"}"style="color: ${sucesso ? "#00c853" : "red"};width: 20px;height: 20px;"
        ></i>
        ${resposta.mensagem}
    `;
    container.appendChild(mensagem);
    lucide.createIcons();
}
function mostrarMensagemEReload(resposta) {
    sessionStorage.setItem(
        "mensagem_reload",
        JSON.stringify({
            status: resposta.status,
            mensagem: resposta.mensagem
        })
    );
    mostrarMensagem2(resposta);
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
      const dados = await response.json();
      mostrarMensagem2(dados);
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
async function filtrarProduto() {
    try {
      const idProduto = document.querySelector('.inputIdProduto').value;
      const csrfToken = getCsrfToken();
      const headers = {
        'Content-Type' : 'application/json',
        'X-CSRFToken' : csrfToken
      }
      const init = {
        method:'GET',
        headers:headers,
      }
    const response = await fetch(`/filtrar-produto/${idProduto}/`, init);
    const data = await response.json();
    mostrarMensagem2(data);
    if (data.status === "erro") {
        return;
    }
    produtos = data.produto;
    cores = data.cores;
    images = data.images;
    console.log(data);
    } catch (e) {
        return;
    }
    const container = document.querySelector(".produtoContainer");
    container.innerHTML = "";
    produtos.forEach(produto => {
        container.appendChild(criarPainelProduto(produto));
    });
}
const filtrarProdutobtn = document.querySelector('.filtrarProdutobtn');
if(filtrarProdutobtn){
  const btnEditar = document.querySelector(".btnEditar");
  const btnExcluir = document.querySelector(".btnExcluir");
  const btnSalvar = document.querySelector(".btnSalvar");
  filtrarProdutobtn.addEventListener('click', function(){
    btnEditar.style.display = "block";
    btnExcluir.style.display = "block";
    btnSalvar.style.display = "block";
    filtrarProduto()
  })
}
function criarPainelProduto(produto) {
    const card = document.createElement("section");
    card.dataset.id = produto.id;
    card.className = "produtoERP";
    card.innerHTML = `
        <div class="erpBody">
            <div class="erpLeft">
                <div class="imagemPrincipal">
                </div>
            </div>
            <div class="erpRight">
                <div class="gridProduto">
                </div>
            </div>
        </div>
        <div class="erpTabs">
            <button class="active">
                Produto
            </button>
            <button>
                Cores
            </button>
            <button>
                Imagens
            </button>
        </div>
        <div class="erpContent">
            <div class="tabProduto"></div>
            <div class="tabCores hidden"></div>
            <div class="tabImagens hidden"></div>
        </div>
    `;
    preencherImagem(card, produto);
    preencherProduto(card, produto);
    preencherCores(card, produto);
    preencherImagens(card, produto);
    configurarAbas(card);
    return card;
}
function criarPainelNovoProduto() {
  const card = document.createElement("section");
  card.className = "produtoERP";
  card.innerHTML = `
      <div class="erpBody">
          <div class="erpLeft">
              <div class="imagemPrincipal"></div>
          </div>
          <div class="erpRight">
              <div class="gridProduto"></div>
          </div>
      </div>
      <div class="erpTabs">
          <button class="active">Produto</button>
          <button>Cores</button>
          <button>Imagens</button>
      </div>
      <div class="erpContent">
          <div class="tabProduto"></div>
          <div class="tabCores hidden"></div>
          <div class="tabImagens hidden"></div>
      </div>
  `;
  const produtoVazio = {
    codigo: "",
    valor: "",
    quantidade: "",
    peso: "",
    altura: "",
    largura: "",
    comprimento: "",
    volume: "",
    categoria: "",
    ativo: "",
    descricao: ""
  };
  cores = [];
  images = [];
  preencherImagem(card, produtoVazio);
  preencherProduto(card, produtoVazio);
  preencherCores(card, produtoVazio);
  preencherImagens(card, produtoVazio);
  configurarAbas(card);
  card.querySelectorAll("input, textarea").forEach(input => {
      input.disabled = false;
  });
  return card;
}
function configurarAbas(card) {
    const botoes = card.querySelectorAll(".erpTabs button");
    const tabs = [
        card.querySelector(".tabProduto"),
        card.querySelector(".tabCores"),
        card.querySelector(".tabImagens")
    ];
    function ativarAba(index) {
        botoes.forEach((btn, i) => {
            btn.classList.toggle("active", i === index);
        });

        tabs.forEach((tab, i) => {
            tab.classList.toggle("hidden", i !== index);
        });
    }
    botoes.forEach((btn, index) => {
        btn.addEventListener("click", () => ativarAba(index));
    });
    ativarAba(0);
}
function preencherImagem(card, produto){
    const div = card.querySelector(".imagemPrincipal");
    const img = images.find(i => i.codigo == produto.codigo);
    div.innerHTML = img
        ? `<img src="${img.imagem}">`
        : `<div class="semImagem">
                Sem imagem
           </div>`;

}
function criarInput(label, valor, classe, tipo = "text") { 
    if (tipo === "checkbox") { 
        return ` 
        <div class="inputBox checkboxBox"> 
            <label>${label}</label> 
            <input type="checkbox" class="${classe} inputProduto" ${valor ? "checked" : ""} disabled> 
        </div> `; 
    } 
    return ` 
    <div class="inputBox"> 
        <label>${label}</label> 
        <input type="${tipo}" class="${classe} inputProduto" value="${valor ?? ""}" disabled> 
    </div> `; 
}
function ativarInputs(inputs){
  inputs.forEach(input =>{
    input.disabled = false;
  });
}
try{
  document.querySelector(".btnEditar").addEventListener("click", () => {
    const card = document.querySelector(".produtoERP");
    if(!card) return;
    ativarInputs(card.querySelectorAll(".inputProduto"));
    const descricao = card.querySelector(".descricao");
    if(descricao)
        descricao.disabled = false;
  });
  document.querySelector(".btnNovo").addEventListener("click", () => {
    const container = document.querySelector(".produtoContainer");
    container.innerHTML = "";
    container.appendChild(
        criarPainelNovoProduto()
    );
    const btnSalvar = document.querySelector('.btnSalvar');
    btnSalvar.style.display = "block";
    const btnEditar = document.querySelector(".btnEditar");
    const btnExcluir = document.querySelector(".btnExcluir");
    btnEditar.style.display = "none";
    btnExcluir.style.display = "none";
  });
} catch(e){
  
}
function preencherProduto(card, produto){
    const div = card.querySelector(".tabProduto");
    div.innerHTML =
        criarInput("Código",produto.codigo,"codigo")+
        criarInput("Valor",produto.valor,"valor")+
        criarInput("Em promoção", produto.is_sale, "is_sale", "checkbox")+
        criarInput("Valor promoção",produto.sale_value,"valorPromocao")+
        criarInput("Peso(kg)",produto.peso,"peso")+
        criarInput("Altura(cm)",produto.altura,"altura")+
        criarInput("Largura(cm)",produto.largura,"largura")+
        criarInput("Comprimento(cm)",produto.comprimento,"comprimento")+
        criarInput("Volume(L)",produto.volume,"volume")+
        criarInput("Categoria",Array.isArray(produto.categoria)? produto.categoria.join(", "): produto.categoria,"categoria","categoria")+
        criarInput("Ativo",produto.ativo,"ativo", "checkbox")+`
        <div class="inputBox full">
            <label>Descrição</label>
            <textarea disabled class="descricao">${produto.descricao}</textarea>
        </div>
    `;
}
function preencherCores(card, produto){
    const div = card.querySelector(".tabCores");
    const lista = cores.filter(c=>c.produtoRef==produto.codigo);
    div.innerHTML = "";
    lista.forEach(cor=>{
        console.log(cor)
        div.innerHTML += `
            <div class="linhaCor" data-id="${cor.id_cor}">
                <div class="inputBox checkboxBox">
                    <input type="checkbox" class="ativo is_ativo inputProduto" ${cor.ativo ? "checked" : ""} disabled>
                </div>
                <span class="circulo" style="background:${cor.cor.startsWith("#") ? cor.cor : "#"+cor.cor}"></span>
                <input class="inputCor" value="${cor.cor}" disabled>
                <input class="inputNomeCor" value="${cor.nome || ""}" placeholder="Nome da cor" disabled>
                <input class="inputQuantidadeCor" type="number"min="0"value="${cor.quantidade}"disabled>
                <button class="btnEditarCor">Editar</button>
                <button class="btnExcluirCor">Excluir</button>
            </div>
        `;
    });
    div.innerHTML += `<button class="btnNovaCor">+ Nova cor</button>`;
    div.querySelector(".btnNovaCor").onclick = criarNovaCor;
    div.querySelectorAll(".btnEditarCor").forEach(btn=>{
        btn.onclick = ()=>editarCor(btn);
    });
    div.querySelectorAll(".btnExcluirCor").forEach(btn => {
        btn.onclick = () => {
            const linha = btn.closest(".linhaCor");
            excluirCor(linha.dataset.id);
        };
    });
}
function criarNovaCor(){
    const div = document.querySelector(".tabCores");
    const linha = document.createElement("div");
    linha.className = "linhaCor";
    linha.innerHTML = `
        <span class="circulo"></span>
        <div class="inputBox checkboxBox">
            <input type="checkbox" class="ativo is_ativo inputProduto" checked=""> 
        </div>
        <input class="inputCor" placeholder="Digite a cor">
        <input class="inputNomeCor"type="text"placeholder="Nome da cor">
        <input class="inputQuantidadeCor" type="number"  min="0"  value="0" placeholder="Quantidade">
        <button class="btnSalvarCor">Salvar</button>
        <button class="btnCancelarCor">Cancelar</button>
    `;
    const input = linha.querySelector(".inputCor");
    const circulo = linha.querySelector(".circulo");
    atualizarPreviewCor(input,circulo);
    linha.querySelector(".btnSalvarCor").onclick = ()=>salvarCor(linha);
    linha.querySelector(".btnCancelarCor").onclick = ()=>linha.remove();
    div.insertBefore(linha,div.querySelector(".btnNovaCor"));
}
async function salvarCor(linha){
    const id = linha.dataset.id || null;
    const metodo = id ? "PUT" : "POST";
    const dados = {
        id: id,
        ativo: linha.querySelector(".is_ativo").checked,
        produto: document.querySelector(".codigo").value,
        nome: linha.querySelector(".inputNomeCor").value,
        cor: linha.querySelector(".inputCor").value,
        quantidade: linha.querySelector(".inputQuantidadeCor").value
      };
    try{
        const csrfToken = getCsrfToken();
        const headers = {
          'Content-Type' : 'application/json',
          'X-CSRFToken' : csrfToken
        }
        const init = {
          method:metodo,
          headers:headers,
          body:JSON.stringify(dados)
        }
        const response = await fetch("/cadastrar-cor/", init);
        const data = await response.json();
        if(data.status == "ok"){
            filtrarProduto();
        }
        mostrarMensagem2(data);
        if (data.status === "erro") {
            return;
        }
    }catch(e){
        console.error(e);
        return;
    }
}
function editarCor(btn){
    const linha = btn.closest(".linhaCor");
    const inputNome = linha.querySelector(".inputNomeCor");
    const inputCor = linha.querySelector(".inputCor");
    const inputQuantidade = linha.querySelector(".inputQuantidadeCor");
    const checkboxAtivo = linha.querySelector(".is_ativo");
    const circulo = linha.querySelector(".circulo");
    const nomeOriginal = inputNome.value;
    const valorOriginal = inputCor.value;
    const quantidadeOriginal = inputQuantidade.value;
    const ativoOriginal = checkboxAtivo.checked;
    inputNome.disabled = false;
    inputCor.disabled = false;
    inputQuantidade.disabled = false;
    checkboxAtivo.disabled = false;
    inputNome.focus();
    atualizarPreviewCor(inputCor, circulo);
    const btnExcluir = linha.querySelector(".btnExcluirCor");
    btn.textContent = "Salvar";
    btnExcluir.textContent = "Cancelar";
    btn.onclick = () => salvarCor(linha);
    btnExcluir.onclick = () => {
        inputNome.value = nomeOriginal;
        inputCor.value = valorOriginal;
        inputQuantidade.value = quantidadeOriginal;
        checkboxAtivo.checked = ativoOriginal;
        circulo.style.backgroundColor =
            valorOriginal.startsWith("#")
                ? valorOriginal
                : "#" + valorOriginal;
        inputNome.disabled = true;
        inputCor.disabled = true;
        inputQuantidade.disabled = true;
        checkboxAtivo.disabled = true;
        btn.textContent = "Editar";
        btnExcluir.textContent = "Excluir";
        btn.onclick = () => editarCor(btn);
        btnExcluir.onclick = () => {
            excluirCor(linha.dataset.id);
        };
    };
}
function atualizarPreviewCor(input, circulo){
    input.oninput = () => {
        let cor = input.value.trim();
        if(/^[0-9A-Fa-f]{6}$/.test(cor))
            cor = "#" + cor;
        circulo.style.backgroundColor = cor;
    };
}
async function excluirCor(id){
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
        const response = await fetch(`/cadastrar-cor/${id}/`,init);
        const data = await response.json();
        if(data.status === "ok"){
          filtrarProduto();
        } 
        mostrarMensagem2(data);
        if (data.status === "erro") {
            return;
        }
  } catch(e){
    console.log(e);
    return;
  }
}
function preencherImagens(card, produto){
    const div = card.querySelector(".tabImagens");
    const lista = images.filter(img => img.codigo == produto.codigo);
    div.innerHTML = "";
    lista.forEach(img=>{
        div.innerHTML += `
            <div class="linhaImagem" data-id="${img.id_image}">
                <img src="${img.imagem}" class="miniImg">
                <select class="selectCorImagem" disabled>
                    ${cores
                        .filter(c=>c.produtoRef==produto.codigo)
                        .map(c=>`
                            <option value="${c.id_cor}"
                                ${c.id_cor == img.id_cor ? "selected":""}>
                                ${c.nome}
                            </option>
                        `).join("")}
                </select>
                <input type="file" class="inputImagem" hidden accept="image/*">
                <button class="btnEditarImagem">Editar</button>
                <button class="btnExcluirImagem">Excluir</button>
            </div>
        `;
    });
    div.innerHTML += `
        <button class="btnNovaImagem">
            + Nova imagem
        </button>
    `;
    div.querySelector(".btnNovaImagem").onclick = ()=>{
        criarNovaImagem(produto);
    };
    div.querySelectorAll(".btnEditarImagem").forEach(btn=>{
        btn.onclick = ()=>editarImagem(btn);
    });
    div.querySelectorAll(".btnExcluirImagem").forEach(btn=>{
        btn.onclick = ()=>excluirImagem(btn);
    });
}
function criarNovaImagem(produto){
    const div = document.querySelector(".tabImagens");
    const linha = document.createElement("div");
    linha.className = "linhaImagem";
    linha.innerHTML = `
        <img class="miniImg">
        <select class="selectCorImagem">
            ${cores
                .filter(c=>c.produtoRef==produto.codigo)
                .map(c=>`
                    <option value="${c.id_cor}">
                        ${c.nome}
                    </option>
                `).join("")}
        </select>
        <input type="file" class="inputImagem" accept="image/*">
        <button class="btnSalvarImagem"> Salvar </button>
        <button class="btnCancelarImagem">Cancelar</button>
    `;
    div.insertBefore(linha, div.querySelector(".btnNovaImagem"));
    const img = linha.querySelector(".miniImg");
    const input = linha.querySelector(".inputImagem");
    input.onchange = ()=>{
        if(input.files.length){
            img.src = URL.createObjectURL(input.files[0]);
        }
    };
    linha.querySelector(".btnSalvarImagem").onclick = ()=>{
        salvarImagem(linha);
    };
    linha.querySelector(".btnCancelarImagem").onclick = ()=>{
        linha.remove();
    };
}
function editarImagem(btn){
    const linha = btn.closest(".linhaImagem");
    const input = linha.querySelector(".inputImagem");
    const select = linha.querySelector(".selectCorImagem");
    const img = linha.querySelector(".miniImg");
    select.disabled = false;
    input.hidden = false;
    input.onchange = ()=>{
        if(input.files.length){
            img.src = URL.createObjectURL(input.files[0]);
        }
    };
    btn.textContent = "Salvar";
    btn.onclick = ()=>{
        salvarImagem(linha);
    };
}
async function excluirImagem(btn){
    const linha = btn.closest(".linhaImagem");
    const id = linha.dataset.id;
    try{
        const csrfToken = getCsrfToken();
        const headers = {
        'X-CSRFToken' : csrfToken
        }
        const init = {
        method:'DELETE',
        headers:headers,
        }
        const response = await fetch(`/cadastrar-imagem/${id}/`,init)
        const data = await response.json();
        if(data.status == "ok"){
            filtrarProduto();
        }
        mostrarMensagem2(data);
        if (data.status === "erro") {
            return;
        }
    }catch(e){
        console.error(e);
        return;
    }
}
async function salvarImagem(linha){
    const id = linha.dataset.id || null;
    const metodo = "POST";
    const form = new FormData();
    form.append(
        "produto",
        document.querySelector(".codigo").value
    );
    form.append(
        "cor",
        linha.querySelector(".selectCorImagem").value
    );
    if(id){
        form.append("id", id);
    }
    const arquivo = linha.querySelector(".inputImagem").files[0];
    if(arquivo){
        form.append("imagem", arquivo);
    }
    try{
        const init = {
            method: metodo,
            headers:{
                "X-CSRFToken":getCsrfToken()
            },
            body: form
        };
        const response = await fetch("/cadastrar-imagem/", init);
        const data = await response.json();
        if(data.status=="ok"){
            filtrarProduto();
        }
        mostrarMensagem2(data);
        if (data.status === "erro") {
            return;
        }
    }catch(e){
        console.error(e);
    }
}
async function salvarProduto() {
    const card = document.querySelector(".produtoERP");
    const id = card.dataset.id || null;
    const dados = {
        id: id,
        codigo: card.querySelector(".codigo").value,
        valor: card.querySelector(".valor").value,
        is_sale: card.querySelector(".is_sale").checked,
        valorPromocao: card.querySelector(".valorPromocao").value,
        altura: card.querySelector(".altura").value,
        largura: card.querySelector(".largura").value,
        comprimento: card.querySelector(".comprimento").value,
        volume: card.querySelector(".volume").value,
        categoria: card.querySelector(".categoria").value,
        ativo: card.querySelector(".ativo").checked,
        peso: card.querySelector(".peso").value,
        descricao: card.querySelector(".descricao").value
    };
    const metodo = id ? "PUT" : "POST";
    try {
        const csrfToken = getCsrfToken();
        const headers = {
          'Content-Type' : 'application/json',
          'X-CSRFToken' : csrfToken
        }
        const init = {
          method:metodo,
          headers:headers,
          body:JSON.stringify(dados)
        }
        const response = await fetch("/cadastrar-produto/",init);
        const data = await response.json();
        if(data.status === "ok"){
            window.location.href = data.redirect_url;
        }
        mostrarMensagem2(data);
        if (data.status === "erro") {
            return;
        }
    } catch(e){
        console.error(e);
        return;
    }
}
try{
  const btnSalvar = document.querySelector('.btnSalvar');
  btnSalvar.addEventListener('click',function(){
    console.log("clicado")
    salvarProduto();
  })
} catch(e){
  
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
        mostrarMensagem2(data);
        if (data.status === "erro") {
            return;
        }
    } catch(e){
        return;
    }
}
try{
  const btnExcluir = document.querySelector('.btnExcluir');
  btnExcluir.addEventListener('click',function(){
    const card = document.querySelector(".produtoERP");
    const id = card.dataset.id;
    deletarProduto(id);
  })
} catch(e){
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
document.addEventListener("DOMContentLoaded", () => {
  try{
    getJsonDetalhes();
  } catch(e){
    console.log(e);
  }
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
let produtoPaginaDetalhes;
let coresPaginaDetalhes;
let imagensPaginaDetalhes;
function getJsonDetalhes() {
  try {
    produtoPaginaDetalhes = JSON.parse(document.getElementById("jsonProdutos").textContent);
    coresPaginaDetalhes = JSON.parse(document.getElementById("jsonCores").textContent);
    imagensPaginaDetalhes = JSON.parse(document.getElementById("jsonImages").textContent);
  } catch (e) {
    return;
  }
  if(produtoPaginaDetalhes && coresPaginaDetalhes && imagensPaginaDetalhes){
    renderProduto();
    renderCores();
    renderImagemInicial();
  }
}
function renderProduto() {
    const nomeEl = document.querySelector(".nomeProduto");
    const categoriasEl = document.querySelector(".categoriasContainer");
    const descricaoEl = document.querySelector(".descricaoProduto");
    const valorEl = document.querySelector(".valorProduto");
    let nome = "Produto sem nome";
    if (produtoPaginaDetalhes.categoria) {
        const categorias = produtoPaginaDetalhes.categoria
            .split(",")
            .map(categoria => categoria.trim())
            .filter(categoria => categoria !== "");
        if (categorias.length > 0) {
            nome = categorias[0];
        }
        categoriasEl.innerHTML = "";
        categorias.slice(1).forEach(categoria => {
            const tag = document.createElement("span");
            tag.className = "categoriaTag";
            tag.textContent = categoria;
            categoriasEl.appendChild(tag);
        });
    }
    nomeEl.textContent = nome;
    descricaoEl.textContent = produtoPaginaDetalhes.descricao || "Sem descrição";
    const valor = Number(produtoPaginaDetalhes.valor);
    const saleValue = Number(produtoPaginaDetalhes.sale_value);
    const precoAntigoEl = document.querySelector(".precoDetalheAntigo");
    const precoPromocionalEl = document.querySelector(".valorProduto");
    const descontoEl = document.querySelector(".descontoDetalhe");
    if (!isNaN(valor)) {
        if (produtoPaginaDetalhes.is_sale === true && !isNaN(saleValue) && saleValue > 0 && saleValue < valor) {
            precoAntigoEl.textContent = valor.toLocaleString("pt-BR", {
                style: "currency",
                currency: "BRL"
            });
            precoPromocionalEl.textContent = saleValue.toLocaleString("pt-BR", {
                style: "currency",
                currency: "BRL"
            });
            const desconto = Math.round(((valor - saleValue) / valor) * 100);
            descontoEl.textContent = `-${desconto}%`;
            descontoEl.style.display = "inline-flex";
        } else {
            precoAntigoEl.textContent = "";
            precoPromocionalEl.textContent = valor.toLocaleString("pt-BR", {
                style: "currency",
                currency: "BRL"
            });
            descontoEl.textContent = "";
            descontoEl.style.display = "none";
        }
    } else {
        precoAntigoEl.textContent = "";
        precoPromocionalEl.textContent = "Preço indisponível";
        descontoEl.textContent = "";
        descontoEl.style.display = "none";
    }
    const carrinhoContainer = document.querySelector(".carrinhoContainer");
    const botaoCarrinho = document.createElement("button");
    botaoCarrinho.className = "addCarrinhoBtn";
    botaoCarrinho.type = "button";
    botaoCarrinho.id = produtoPaginaDetalhes.id;
    botaoCarrinho.innerHTML = ` <i data-lucide="shopping-cart"></i> Adicionar ao carrinho`;
    carrinhoContainer.appendChild(botaoCarrinho);
    if (window.lucide) {
        lucide.createIcons();
    }
    botaoCarrinho.addEventListener('click', function(){
      const id = this.id;
      addToCart(id)
    })
    const volumeContainer = document.querySelector(".volumeContainer");
    const volumeProduto = document.querySelector(".volumeProduto");
    const altura = produtoPaginaDetalhes.altura;
    const largura = produtoPaginaDetalhes.largura;
    const comprimento = produtoPaginaDetalhes.comprimento;
    const volume = produtoPaginaDetalhes.volume;
    if (altura || largura || comprimento || volume) {
        volumeContainer.style.display = "block";
        volumeProduto.innerHTML = `
            <strong>Dimensões:</strong><br>
            Altura: ${altura || 0} cm<br>
            Largura: ${largura || 0} cm<br>
            Comprimento: ${comprimento || 0} cm
            ${volume ? `<br><br><strong>Volume:</strong> ${volume} ml` : ""}
        `;
    } else {
        volumeContainer.style.display = "none";
    }
}
let corSelecionadaId = null;
function renderCores() {
    const container = document.querySelector(".coresContainer");
    const quantidadeEl = document.querySelector(".quantidadeCor");
    container.innerHTML = "";
    coresPaginaDetalhes.forEach(cor => {
        const btn = document.createElement("div");
        btn.className = "corProduto";
        const codigoCor = cor.cor.startsWith("#") ? cor.cor : `#${cor.cor}`;
        btn.style.backgroundColor = codigoCor;
        btn.addEventListener("click", () => {
            trocarImagem(cor.id_cor);
            container.querySelectorAll(".corProduto").forEach(c => {
                c.classList.remove("selecionada");
            });
            btn.classList.add("selecionada");
            corSelecionadaId = cor.id_cor;
            atualizarQuantidadeCor(cor);
            console.log("Cor selecionada:", cor);
        });
        container.appendChild(btn);
    });
    if (coresPaginaDetalhes.length > 0) {
        const primeiraCor = coresPaginaDetalhes[0];
        const primeiroBotao = container.querySelector(".corProduto");
        if (primeiroBotao) {
            primeiroBotao.classList.add("selecionada");
        }
        corSelecionadaId = primeiraCor.id_cor;
        atualizarQuantidadeCor(primeiraCor);
    }
}
function atualizarQuantidadeCor(cor) {
    const quantidadeEl = document.querySelector(".quantidadeCor");
    if (!quantidadeEl) return;
    const quantidade = Number(cor.quantidade) || 0;
    if (quantidade > 0) {
        quantidadeEl.textContent =`${quantidade} ${quantidade === 1 ? "unidade" : "unidades"} disponíveis`;
    } else {
        quantidadeEl.textContent = "Produto esgotado";
    }
}
function renderImagemInicial() {
    if (coresPaginaDetalhes.length > 0) {
        const primeiraCor = coresPaginaDetalhes[0];
        trocarImagem(primeiraCor.id_cor);
        corSelecionadaId = primeiraCor.id_cor;
        const primeiraBolinha = document.querySelector(`.corProduto[data-id="${primeiraCor.id_cor}"]`);
        if (primeiraBolinha) {
            primeiraBolinha.classList.add("selecionada");
        }
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
try{
  document.querySelectorAll('.accordionHeader').forEach(header => {
    header.addEventListener('click', () => {
      const item = header.closest('.accordionItem');
      const body = item.querySelector('.accordionBody');
      const isOpen = item.classList.contains('open');
      if (isOpen) {
        body.style.maxHeight = null;
        item.classList.remove('open');
      } else {
        item.classList.add('open');
        body.style.maxHeight = body.scrollHeight + 'px';
      }
    });
  });
} catch(e){
  console.log(e);
}
const sliderRadios = document.querySelectorAll('.slides input[type="radio"]');
const textosContainer = document.querySelector('.textos');
if (sliderRadios.length && textosContainer) {
  sliderRadios.forEach(function (radio) {
    radio.addEventListener('change', function () {
      textosContainer.classList.toggle('showText2', radio.id === 'radio2' && radio.checked);
    });
  });
}
async function addToCart(produtoId) {
    if (corSelecionadaId === null) { 
      const json = {
        "status": "erro",
        "mensagem": "Selecione uma cor"
      }
      mostrarMensagem2(json);
      return; 
    }
    try {
        const csrfToken = getCsrfToken();
        const headers = {
        'Content-Type' : 'application/json',
        'X-CSRFToken' : csrfToken
        }
        const init = {
        method:'POST',
        headers:headers,
        body: JSON.stringify({
            produto_id: produtoId,
            cor_id: corSelecionadaId
        })
        }
        const response = await fetch("/carrinho/", init);
        const dados = await response.json();
        if(dados.status==="ok"){
            window.location.reload();
        }
        mostrarMensagemEReload(dados);
        if (dados.status === "erro") {
            return;
        }
    } catch (e) {
        console.error(e);
        return;
    }
}
async function alterarQuantidade(input,alteracao) {
    const produtoId = input.dataset.productId;
    const corId = input.dataset.colorId;
    const selector = input.closest(".cartItemQuantity");
    const quantidadeEl = selector.querySelector(".quantityValue");
    let quantidade = parseInt(quantidadeEl.textContent);
    const maxQuantidade = parseInt(quantidadeEl.dataset.max);
    const novaQuantidade = quantidade + alteracao;
    if (novaQuantidade < 1) {
        return;
    }
    if (novaQuantidade > maxQuantidade) {
        return;
    }
    quantidadeEl.textContent = novaQuantidade;
    try {
        const csrfToken = getCsrfToken();
        const headers = {
        'Content-Type' : 'application/json',
        'X-CSRFToken' : csrfToken
        }
        const init = {
        method:'PUT',
        headers:headers,
        body: JSON.stringify({
            produto_id: produtoId,
            cor_id: corId,
            quantidade: novaQuantidade
        })
        }
        const response = await fetch("/carrinho/", init);
        const dados = await response.json();
        if (dados.status === "erro") {
            return;
        }
        window.location.reload()
    } catch (e) {
        console.error(e);
        return;
    }
}
async function removerDoCarrinho(produtoId,corId) {
    try {
        const csrfToken = getCsrfToken();
        const headers = {
        'Content-Type' : 'application/json',
        'X-CSRFToken' : csrfToken
        }
        const init = {
        method:'DELETE',
        headers:headers,
        body: JSON.stringify({
                produto_id: produtoId,
                cor_id: corId
            })
        }
        const response = await fetch("/carrinho/", init);
        const dados = await response.json();
        mostrarMensagem2(dados);
        if (dados.status === "erro") {
            return;
        }
        const card = document.querySelector(
            `.cartItem[data-product-id="${produtoId}"][data-color-id="${corId}"]`
        );
        if (card) {card.remove();}
        const itens = document.querySelectorAll(".cartItem");
        if (itens.length === 0) {window.location.reload();}
    } catch (e) {
        console.error(e);
        return;
    }
}
document.querySelectorAll(".cartItemRemove").forEach(button => {
    button.addEventListener("click", () => {
        const produtoId = button.dataset.productId;
        const corId = button.dataset.colorId;
        removerDoCarrinho(
            produtoId,
            corId
        );
    });
});
document.querySelectorAll(".quantityMinus").forEach(button => {
    button.addEventListener("click", () => {
        alterarQuantidade(button, -1);
    });
});
document.querySelectorAll(".quantityPlus").forEach(button => {
    button.addEventListener("click", () => {
        alterarQuantidade(button, 1);
    });
});
async function calcularFreteProduto() {
    const cepInput =document.querySelector("#cepProduto");
    const resultado =document.querySelector("#resultadoFrete");
    const cep = cepInput.value.replace(/\D/g, "");
    if (cep.length !== 8) {
        const dados = {
            'status' : 'erro',
            'mensagem' : 'CEP inválido.' 
        }
        mostrarMensagem2(dados);
        return;
    }
    const produtoId = produtoPaginaDetalhes.id;
    try {
        const csrfToken = getCsrfToken();
        const headers = {
        'Content-Type' : 'application/json',
        'X-CSRFToken' : csrfToken
        }
        const init = {
        method:'POST',
        headers:headers,
        body: JSON.stringify({
                produto_id:produtoId,
                cep:cep
            })
        }
        const response = await fetch("/calcular-frete-produto/",init)
        const dados = await response.json();
        mostrarMensagem2(dados);
        if (dados.status === "erro") {
            return;
        }
        renderizarOpcoesFrete(dados.opcoes);
    } catch (erro) {
        console.log(erro);
        resultado.innerHTML = `<p>Erro ao calcular o frete.</p>`;
    }
}
function renderizarOpcoesFrete(opcoes) {
    const container = document.querySelector("#opcoesFrete");
    if (!container) {
        console.error("Container #opcoesFrete não encontrado.");
        return;
    }
    container.innerHTML = "";
    if (!Array.isArray(opcoes)) {
        console.error("Opções de frete não são um array:", opcoes);
        return;
    }
    const opcoesValidas = opcoes.filter(opcao => !opcao.error);
    if (opcoesValidas.length === 0) {
        container.innerHTML = `
            <p class="freteSemOpcoes">
                Nenhuma opção de frete disponível para este CEP.
            </p>
        `;
        return;
    }
    const menorPrazo = Math.min(
        ...opcoesValidas.map(opcao =>
            Number(
                opcao.custom_delivery_time ??
                opcao.delivery_time ??
                opcao.prazo
            )
        )
    );
    opcoesValidas.forEach(opcao => {
        const prazo = Number(opcao.custom_delivery_time ?? opcao.delivery_time ??opcao.prazo);
        const preco = Number(opcao.custom_price ?? opcao.price ?? opcao.preco);
        const logoUrl = opcao.company?.picture || opcao.logo || "";
        const badgeFast = prazo === menorPrazo
            ? `
                <span class="frete-badge-fast">
                    <i data-lucide="zap" class="icon-fast"></i>
                    Fast
                </span>
            `
            : "";
        const div = document.createElement("div");
        div.className = "opcaoFrete";
        div.innerHTML = `
            <div class="freteOpcaoInfo">
                ${
                    logoUrl ? `<img src="${logoUrl}"alt="${opcao.name}"class="frete-logo">`: ""
                }
                <div class="freteDetalhes">
                    <small>Prazo: ${prazo} dias úteis</small>
                    <p class="fretePreco">
                        R$ ${preco.toLocaleString("pt-BR", {
                            minimumFractionDigits: 2
                        })}
                    </p>
                </div>
                ${badgeFast}
            </div>
        `;
        if (document.querySelector("#freteContainer")) {
            div.addEventListener("click", () => {
                selecionarFrete(opcao, div);
            });
        }
        container.appendChild(div);
    });
    if (window.lucide) {lucide.createIcons();}
    const freteAccordion = document.querySelector(".frete");
    if (freteAccordion) {
        const body = freteAccordion.querySelector(".accordionBody");
        if (body) {
            body.style.maxHeight = body.scrollHeight + "px";
        }
    }
    const freteContainer = document.querySelector("#freteContainer");
    if (freteContainer) {
        freteContainer.style.display = "block";
    }
}
let cotacaoFreteSelecionada = null;
let opcaoFreteSelecionada = null;
let valorFreteSelecionado = 0;
function formatarMoeda(valor) {
    return Number(valor).toLocaleString(
        "pt-BR",
        {
            style: "currency",
            currency: "BRL"
        }
    );
}
async function selecionarFrete(opcao,elemento) {
    if (!cotacaoFreteSelecionada){
        alert("Calcule o frete novamente.");
        return;
    }
    document.querySelectorAll(".opcaoFrete").forEach(el => {
            el.classList.remove("selected");
        });
    elemento.classList.add("selected");
    try {
        const csrfToken = getCsrfToken();
        const headers = {
        'Content-Type' : 'application/json',
        'X-CSRFToken' : csrfToken
        }
        const init = {
        method:'POST',
        headers:headers,
        body: JSON.stringify({
                    cotacao_id:cotacaoFreteSelecionada,
                    opcao_id:opcao.id
                })
        }
        const response =await fetch("/selecionar-frete/",init)
        const dados = await response.json();
        mostrarMensagem2(dados);
        if (dados.status === "erro") {
            return;
        }
        opcaoFreteSelecionada = opcao.id;
        valorFreteSelecionado = Number(dados.preco);
        const freteEl =document.querySelector("#cartFrete");
        if (freteEl) { 
            freteEl.textContent = formatarMoeda(valorFreteSelecionado);
        }
        atualizarTotal();
        const checkoutBtn =document.querySelector("#checkoutBtn");
        checkoutBtn.classList.remove("checkoutDisabled");
        checkoutBtn.removeAttribute("aria-disabled");
    } catch (erro) {
        console.error("Erro ao selecionar frete:",erro);
        alert("Erro ao selecionar o frete.");
    }
}
function atualizarTotal() {
    const subtotal = Number(document.querySelector("#cartSubtotal").dataset.value.replace(",", "."));
    const total = subtotal + valorFreteSelecionado;
    document.querySelector("#cartTotal").textContent = formatarMoeda(total);
}
const cepForm = document.querySelector(".cepForm");
if (cepForm) {
    cepForm.addEventListener("submit", async function(event) {
        event.preventDefault();
        const cepInput = document.querySelector("#cep");
        const cep = cepInput.value.trim();
        if (!cep) {
            const json = {
                "status" : "erro",
                "mensagem" : "Digite um CEP válido."
            }
            mostrarMensagem2(json);
            return;
        }
        const csrfToken = getCsrfToken();
        const headers = {
        'Content-Type' : 'application/json',
        'X-CSRFToken' : csrfToken
        }
        const init = {
        method:'POST',
        headers:headers,
        body: JSON.stringify({
                    cep: cep
                })
        }
        try {
            const response = await fetch("/cotar-frete-carrinho/",init);
            const dados = await response.json();
            mostrarMensagem2(dados);
            console.log(dados.r)
            if (dados.status === "erro") {
                return;
            }
            cotacaoFreteSelecionada = dados.cotacao_id
            renderizarOpcoesFrete(dados.opcoes);
        } catch (erro){
            console.error("Erro ao calcular frete:",erro);
            return;
        }
    });
}
async function carregarPedido(id) {
    try {
        const response = await fetch(`/pesquisar-pedido/?codigo=${id}`);
        const dados = await response.json();
        if (dados.status === "erro") {
            mostrarMensagem2(dados);
            return;
        }
        renderizarPedido(dados.pedido);
        mostrarMensagem2(dados);
    } catch (erro) {
        console.error("Erro ao carregar pedido:", erro);
        alert("Erro ao carregar pedido.");
    }
}
async function pesquisarPedido() {
    const input = document.querySelector("#codigoPedido");
    const codigo = input.value.trim();
    if (!codigo) {
        alert("Digite o código do pedido.");
        return;
    }
    await carregarPedido(codigo);
}
function renderizarPedido(pedido) {
    const container = document.querySelector("#pedidoERP");
    if (!container) {
        console.error("Container #pedidoERP não encontrado.");
        return;
    }
    container.innerHTML = `
        <section class="pedidoERPCarte">
            <div class="pedidoERPTopo">
                <div class="pedidoERPIdentificacao">
                    <i data-lucide="package"></i>
                    <div>
                        <h2>Pedido #${pedido.id}</h2>
                        <span>${pedido.criado_em || ""}</span>
                    </div>
                </div>
                <span class="pedidoERPStatus ${classeStatusPedido(pedido.status)}">
                    ${pedido.status_display || pedido.status}
                </span>
            </div>
            <div class="pedidoERPBloco">
                <h3 class="pedidoERPBlocoTitulo">
                    Informações do pedido
                </h3>
                <div class="pedidoERPGrid">
                    ${campoPedidoERP("Cliente",pedido.nome_cliente)}
                    ${campoPedidoERP("E-mail",pedido.email_cliente)}
                    ${campoPedidoERP("Telefone",pedido.telefone_cliente)}
                    ${campoPedidoERP("Subtotal",pedido.subtotal ? `R$ ${pedido.subtotal}` : null)}
                    ${campoPedidoERP("Frete",pedido.frete ? `R$ ${pedido.frete}` : null)}
                    ${campoPedidoERP("Total",pedido.total ? `R$ ${pedido.total}` : null)}
                    ${campoPedidoERP("Mercado Pago Preference ID",pedido.mp_preference_id)}
                    ${campoPedidoERP("Mercado Pago Payment ID",pedido.mp_payment_id)}
                    ${campoPedidoERP("Status Mercado Pago",pedido.mp_status)}
                    ${campoPedidoERP("Detalhe pagamento",pedido.mp_status_detail)}
                    ${campoPedidoERP("Data pagamento",pedido.data_pagamento)}
                </div>
            </div>
            ${renderizarEnderecoPedido(pedido)}
            ${renderizarFretePedido(pedido)}
            ${renderizarItensPedido(pedido)}
            ${renderizarRastreamentoPedido(pedido)}
            ${renderizarRetiradaPedido(pedido)}
            ${renderizarTimelinePedido(pedido)}
            ${renderizarAcoesPedido(pedido)}
        </section>
    `;
    if (window.lucide) {
        lucide.createIcons();
    }
}
function renderizarRetiradaPedido(pedido) {
    if (pedido.opcao_frete_id !== null && pedido.opcao_frete_id !== undefined) {
        return "";
    }

    return `
        <div class="pedidoERPBloco">
            <h3 class="pedidoERPBlocoTitulo">Retirada</h3>
            <div class="pedidoERPGrid">
                ${campoPedidoERP("Modalidade", "Retirada na loja")}
            </div>
        </div>
    `;
}
function campoPedidoERP(label, valor) {
    if (valor === null || valor === undefined || valor === "") return ""
    return `
        <div class="pedidoERPInfo">
            <label>${label}</label>
            <span title="${valor}">${valor}</span>
        </div>
    `;
}
function classeStatusPedido(status) {
    switch (status) {
        case "pago":return "pago";
        case "enviado":return "enviado";
        case "entregue":return "entregue";
        case "cancelado":return "cancelado";
        default: return "";
    }
}
function renderizarEnderecoPedido(pedido) {
    const campos = [
        ["CEP", pedido.cep],
        ["Endereço", pedido.endereco],
        ["Número", pedido.numero],
        ["Complemento", pedido.complemento],
        ["Bairro", pedido.bairro],
        ["Cidade", pedido.cidade],
        ["Estado", pedido.estado]
    ];
    const html = campos
        .filter(([_, valor]) =>
            valor !== null &&
            valor !== undefined &&
            valor !== ""
        )
        .map(([label, valor]) =>
            campoPedidoERP(label, valor)
        )
        .join("");
    if (!html) {
        return "";
    }
    return `
        <div class="pedidoERPBloco">
            <h3 class="pedidoERPBlocoTitulo">Endereço de entrega</h3>
            <div class="pedidoERPGrid">
                ${html}
            </div>
        </div>
    `;
}
function renderizarFretePedido(pedido) {
    if (pedido.opcao_frete_id === null || pedido.opcao_frete_id === undefined) {
        return "";
    }

    const campos = [
        ["Transportadora", pedido.transportadora],
        ["Serviço", pedido.servico_frete],
        ["Prazo", pedido.prazo_frete ? `${pedido.prazo_frete} dias` : null],
        ["Cotação", pedido.cotacao_frete_id],
        ["Opção", pedido.opcao_frete_id],
        ["Shipment ID", pedido.melhor_envio_shipment_id],
        ["Order ID", pedido.melhor_envio_order_id]
    ];

    const html = campos
        .filter(([_, valor]) => valor !== null && valor !== undefined && valor !== "")
        .map(([label, valor]) => campoPedidoERP(label, valor))
        .join("");

    if (!html) return "";

    return `
        <div class="pedidoERPBloco">
            <h3 class="pedidoERPBlocoTitulo">Envio</h3>
            <div class="pedidoERPGrid">
                ${html}
            </div>
        </div>
    `;
}
function renderizarItensPedido(pedido) {
    if (!pedido.itens || pedido.itens.length === 0) {return "";}
    return `
        <div class="pedidoERPBloco">
            <h3 class="pedidoERPBlocoTitulo">
                Produtos do pedido
            </h3>
            <div class="pedidoERPItens">
                <div class="pedidoERPItem">
                    <strong>Produto</strong>
                    <strong>Cor</strong>
                    <strong>Qtd.</strong>
                    <strong>Unitário</strong>
                    <strong>Subtotal</strong>
                </div>
                ${pedido.itens.map(item => `
                    <div class="pedidoERPItem">
                        <div class="pedidoERPProduto">
                            <strong>${item.produto}</strong>
                        </div>
                        <div class="pedidoERPItemInfo">
                            ${item.cor || "-"}
                        </div>
                        <div class="pedidoERPItemInfo">
                            ${item.quantidade}
                        </div>
                        <div class="pedidoERPItemPreco">
                            R$ ${item.preco_unitario}
                        </div>
                        <div class="pedidoERPItemPreco">
                            R$ ${item.subtotal}
                        </div>
                    </div>
                `).join("")}
            </div>
            <div class="pedidoERPTotais">
                ${pedido.subtotal
                    ? `
                        <div class="pedidoERPTotalItem">
                            <span>Subtotal</span>
                            <strong>R$ ${pedido.subtotal}</strong>
                        </div>
                    `
                    : ""
                }
                ${pedido.frete
                    ? `
                        <div class="pedidoERPTotalItem">
                            <span>Frete</span>
                            <strong>R$ ${pedido.frete}</strong>
                        </div>
                    `
                    : ""
                }
                ${pedido.total
                    ? `
                        <div class="pedidoERPTotalItem pedidoERPTotalFinal">
                            <span>Total</span>
                            <strong>R$ ${pedido.total}</strong>
                        </div>
                    `
                    : ""
                }
            </div>
        </div>
    `;
}
function renderizarRastreamentoPedido(pedido) {
    if (!pedido.codigo_rastreio && !pedido.etiqueta_url && !pedido.etiqueta_paga) {
        return "";
    }
    let html = "";
    if (pedido.codigo_rastreio) {
        html += campoPedidoERP("Código de rastreio", pedido.codigo_rastreio);
    }
    if (pedido.etiqueta_paga !== null &&
        pedido.etiqueta_paga !== undefined) {
        html += campoPedidoERP("Etiqueta paga", pedido.etiqueta_paga ? "Sim" : "Não");
    }
    if (pedido.etiqueta_url) {
        html += campoPedidoERP("Etiqueta","Disponível");
    }
    if (!html) {
        return "";
    }
    return `
        <div class="pedidoERPBloco">
            <h3 class="pedidoERPBlocoTitulo">
                Rastreamento
            </h3>
            <div class="pedidoERPGrid">
                ${html}
            </div>
        </div>
    `;
}
function renderizarTimelinePedido(pedido) {
    const status = pedido.status;
    const retirada = pedido.opcao_frete_id === null || pedido.opcao_frete_id === undefined;

    const etapas = retirada
        ? [
            ["Pedido", true],
            ["Pagamento", ["pago", "preparando", "pronto_retirada"].includes(status)],
            ["Preparando", ["preparando", "pronto_retirada"].includes(status)],
            ["Pronto para retirada", status === "pronto_retirada"]
        ]
        : [
            ["Pedido", true],
            ["Pagamento", ["pago", "preparando", "etiqueta_gerada", "enviado", "entregue"].includes(status)],
            ["Preparando", ["preparando", "etiqueta_gerada", "enviado", "entregue"].includes(status)],
            ["Etiqueta", ["etiqueta_gerada", "enviado", "entregue"].includes(status)],
            ["Enviado", ["enviado", "entregue"].includes(status)],
            ["Entregue", status === "entregue"]
        ];

    return `
        <div class="pedidoERPBloco">
            <h3 class="pedidoERPBlocoTitulo">
                Andamento do pedido
            </h3>
            <div class="pedidoERPTimeline">
                ${etapas.map((etapa, index) => {
                    const concluido = etapa[1];
                    const ultimo = index === etapas.length - 1;
                    const proximaConcluida = !ultimo && etapas[index + 1][1];

                    return `
                        <div class="pedidoERPEtapa ${concluido ? "concluido" : ""}">
                            <div class="pedidoERPCirculo ${concluido ? "concluido" : ""}">
                                ${concluido ? "✓" : ""}
                            </div>
                            <span>${etapa[0]}</span>
                            ${!ultimo ? `
                                <div class="pedidoERPConector ${proximaConcluida ? "concluido" : ""}"></div>
                            ` : ""}
                        </div>
                    `;
                }).join("")}
            </div>
        </div>
    `;
}
function renderizarAcoesPedido(pedido) {
    const retirada = pedido.opcao_frete_id === null || pedido.opcao_frete_id === undefined;

    let html = `
        <div class="pedidoERPBloco">
            <div class="pedidoERPAcoes">
    `;
    if (retirada) {
    if (pedido.status === "pago") {
        html += `
            <button type="button" onclick="marcarProntoRetirada(${pedido.id}, 'preparando')">
                Começar a preparar
            </button>
        `;
    } else if (pedido.status === "preparando") {
        html += `
            <button type="button" onclick="marcarProntoRetirada(${pedido.id}, 'pronto_retirada')">
                Marcar como pronto para retirada
            </button>
        `;
    }
    }   
     else {
        if (!pedido.etiqueta_paga) {
            html += `
                <a href="/gerar-etiqueta/${pedido.id}/">
                    Gerar e pagar etiqueta
                </a>
            `;
        } else {
            html += `
                <a href="/imprimir-etiqueta/${pedido.id}/" target="_blank">
                    Imprimir etiqueta
                </a>
            `;
        }
        html += `
            <a href="/atualizar-tracking/${pedido.id}/">
                🔄 Atualizar rastreamento
            </a>
        `;
    }
    html += `
            </div>
        </div>
    `;
    return html;
}
async function marcarProntoRetirada(id,status) {
    mostrarLoading();
    try {
        const csrfToken = getCsrfToken();
        const response = await fetch(`/atualizar-status-retirada/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                'pedido_id' : id,
                'status' : status
            })
        });
        const dados = await response.json();
        mostrarMensagem2(dados);
        if (dados.status === "ok") {
            await carregarPedido(id);
        }
    } catch (erro) {
        console.error("Erro ao atualizar status:", erro);
        mostrarMensagem2({
            status: "erro",
            mensagem: "Erro ao atualizar o status do pedido."
        });
    } finally{
        esconderLoading()
    }
}
const btnPedido = document.getElementById("btnBuscarPedidoERP");
if (btnPedido){
    btnPedido.addEventListener("click", function(){
        pesquisarPedido();
    });
}



const inputPesquisa = document.getElementById("inputPesquisa");
const resultadoPesquisa = document.getElementById("resultadoPesquisa");
const limparPesquisa = document.getElementById("limparPesquisa");
let timeoutPesquisa = null;
let controllerPesquisa = null;
function escaparHTML(valor) {
    const div = document.createElement("div");
    div.textContent = valor ?? "";
    return div.innerHTML;
}
function formatarPreco(valor) {
    return Number(valor).toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL"
    });
}
async function pesquisarProdutos(termo) {
    termo = termo.trim();
    if (!termo) {
        fecharPesquisa();
        return;
    }
    if (controllerPesquisa) {
        controllerPesquisa.abort();
    }
    controllerPesquisa = new AbortController();
    resultadoPesquisa.innerHTML = `
        <div class="resultadoPesquisaCarregando">
            Pesquisando...
        </div>
    `;
    resultadoPesquisa.classList.add("aberto");
    try {
        const response = await fetch(
            `/pesquisar-produtos/?q=${encodeURIComponent(termo)}`,
            {
                signal: controllerPesquisa.signal
            }
        );
        if (!response.ok) {
            throw new Error("Erro na pesquisa.");
        }
        const dados = await response.json();
        if (dados.status !== "ok") {
            throw new Error("Erro ao pesquisar produtos.");
        }
        renderizarResultadosPesquisa(dados.produtos,termo);
    } catch (erro) {
        if (erro.name === "AbortError") {
            return;
        }
        console.error("Erro na pesquisa:", erro);
        resultadoPesquisa.innerHTML = `
            <div class="resultadoPesquisaVazio">
                Não foi possível realizar a pesquisa.
            </div>
        `;
    }
}
function renderizarResultadosPesquisa(produtos, termo) {
    if (!produtos || produtos.length === 0) {
        resultadoPesquisa.innerHTML = `
            <div class="resultadoPesquisaVazio">
                Nenhum produto encontrado para
                <strong>"${escaparHTML(termo)}"</strong>.
            </div>
            <a href="/produtos/?busca=${encodeURIComponent(termo)}" class="resultadoPesquisaTodos">
                Ver página de resultados
                <i data-lucide="arrow-right"></i>
            </a>
        `;
        resultadoPesquisa.classList.add("aberto");
        if (window.lucide) {
            lucide.createIcons();
        }
        return;
    }
    
    const produtosHTML = produtos.map(produto => {
        const imagem = produto.imagem
            ? `<img src="${escaparHTML(produto.imagem)}" alt="${escaparHTML(produto.nome)}">`
            : "";
        let blocoPreco = "";
        if (produto.is_sale && produto.preco_antigo) {
            blocoPreco = `
                <span class="resultadoPesquisaPrecoAntigo">
                    ${formatarPreco(produto.preco_antigo)}
                </span>
                <span class="resultadoPesquisaPrecoPromocional">
                    ${formatarPreco(produto.preco)}
                </span>
            `;
        } else {
            blocoPreco = `
                <span class="resultadoPesquisaPrecoNormal">
                    ${formatarPreco(produto.preco)}
                </span>
            `;
        }
        return `
            <a href="/produtos/${encodeURIComponent(produto.codigo)}/" class="resultadoPesquisaItem">
                <div class="resultadoPesquisaImagem">
                    ${imagem}
                </div>
                <div class="resultadoPesquisaInfo">
                    <span class="resultadoPesquisaNome">
                        ${escaparHTML(produto.nome)}
                    </span>
                    <div class="resultadoPesquisaPrecoContainer">
                        ${blocoPreco}
                    </div>
                </div>
            </a>
        `;
    }).join("");
    resultadoPesquisa.innerHTML = `
        ${produtosHTML}
        <a href="/produtos/?busca=${encodeURIComponent(termo)}" class="resultadoPesquisaTodos">
            Ver todos os resultados
            <i data-lucide="arrow-right"></i>
        </a>
    `;
    resultadoPesquisa.classList.add("aberto");
    if (window.lucide) {
        lucide.createIcons();
    }
}
if (inputPesquisa) {
    inputPesquisa.addEventListener("input", function () {
        const termo = this.value.trim();
        limparPesquisa.style.display = termo ? "flex" : "none";
        clearTimeout(timeoutPesquisa);
        if (!termo) {
            fecharPesquisa();
            return;
        }
        timeoutPesquisa = setTimeout(() => {
            pesquisarProdutos(termo);
        }, 300);
    });
    inputPesquisa.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            const termo = this.value.trim();
            if (!termo) return;
            window.location.href =
                `/produtos/?busca=${encodeURIComponent(termo)}`;
        }
        if (event.key === "Escape") {
            fecharPesquisa();
            inputPesquisa.blur();
        }
    });

}
if (limparPesquisa) {
    limparPesquisa.addEventListener("click", function () {
        inputPesquisa.value = "";
        limparPesquisa.style.display = "none";
        fecharPesquisa();
        inputPesquisa.focus();
    });

}
document.addEventListener("click", function (event) {
    const barra = document.getElementById("barraPesquisa");
    if (!barra) return;
    if (!barra.contains(event.target)) {
        fecharPesquisa();
    }
});
function fecharPesquisa() {
    if (!resultadoPesquisa) return;
    resultadoPesquisa.classList.remove("aberto");
}
const params = new URLSearchParams(window.location.search);
if (params.get("melhor_envio") === "conectado") {
    mostrarMensagem2({
        status: "ok",
        mensagem: "Melhor Envio conectado com sucesso."
    });
    window.history.replaceState(
        {},
        document.title,
        window.location.pathname
    );
}