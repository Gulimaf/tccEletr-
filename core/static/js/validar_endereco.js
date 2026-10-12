document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("#checkoutForm");
    if (!form) return;
    const cepInput = document.querySelector("#cep");
    const enderecoInput = document.querySelector("#endereco");
    const bairroInput = document.querySelector("#bairro");
    const cidadeInput = document.querySelector("#cidade");
    const estadoInput = document.querySelector("#estado");
    const mensagem = document.querySelector("#validacaoEndereco");
    const botao = document.querySelector("#btnPagamento");
    let dadosCEP = null;
    function normalizar(valor) {
        return String(valor || "")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .trim()
            .toLowerCase()
            .replace(/\s+/g, " ");
    }
    function erro(mensagemTexto) {
        mensagem.textContent = mensagemTexto;
        mensagem.style.display = "block";
        botao.disabled = true;
        botao.style.opacity = "0.5";
    }
    function sucesso() {
        mensagem.textContent = "";
        mensagem.style.display = "none";
        botao.disabled = false;
        botao.style.opacity = "";
    }
    async function consultarCEP() {
        const cep = cepInput.value.replace(/\D/g, "");
        if (cep.length !== 8) {
            erro("O CEP da cotação é inválido.");
            return false;
        }
        try {
            const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
            if (!response.ok) {
                throw new Error("Erro na consulta.");
            }
            const data = await response.json();
            if (data.erro) {
                erro("O CEP informado não foi encontrado.");
                return false;
            }
            dadosCEP = data;
            return true;
        } catch (e) {
            console.error(e);
            erro("Não foi possível verificar o endereço. Tente novamente.");
            return false;
        }
    }
    function validarEndereco() {
        if (!dadosCEP) {
            return false;
        }
        const cidade = normalizar(cidadeInput.value);
        const estado = normalizar(estadoInput.value);
        const bairro = normalizar(bairroInput.value);
        console.log(bairro)
        const endereco = normalizar(enderecoInput.value);
        const cidadeCEP = normalizar(dadosCEP.localidade);
        const estadoCEP = normalizar(dadosCEP.uf);
        const bairroCEP = normalizar(dadosCEP.bairro);
        const enderecoCEP = normalizar(dadosCEP.logradouro);
        if (cidade !== cidadeCEP) {
            erro(`A cidade não corresponde ao CEP. O CEP pertence a ${dadosCEP.localidade} - ${dadosCEP.uf}.`);
            return false;
        }
        if (estado !== estadoCEP) {
            erro(`O estado não corresponde ao CEP.  O estado correto é ${dadosCEP.uf}.`);
            return false;
        }
        if (bairroCEP && bairro !== bairroCEP) {
            erro(`O bairro não corresponde ao CEP. O bairro correto é ${dadosCEP.bairro}.`);
            return false;
        }
        if (enderecoCEP &&!endereco.includes(enderecoCEP) &&ludes(endereco)) {
            erro(`O endereço não corresponde ao CEP. O logradouro correto é ${dadosCEP.logradouro}.`);
            return false;
        }
        sucesso();
        return true;
    }
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        botao.disabled = true;
        const cepValido = await consultarCEP();
        if (!cepValido) {
            return;
        }
        const enderecoValido = validarEndereco();
        if (!enderecoValido) {
            return;
        }
        form.submit();
    });
});