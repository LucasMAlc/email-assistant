function validateForm() {
    const fileInput = document.querySelector('input[name="file"]');
    const textInput = document.querySelector('textarea[name="text"]');
    if (!fileInput.value && !textInput.value.trim()) {
        showToast("Envie um arquivo ou insira um texto.!");
        return false;
    }
    return true;
}

// Copiar resposta 
function copyResponse() {
    const resposta = document.getElementById("resposta-text").innerText;
    navigator.clipboard.writeText(resposta).then(() => {
        showToast("Resposta copiada!");
    }).catch(err => {
        showToast("Erro ao copiar a resposta.");
    });
}

function showToast(msg) {
    const toast = document.getElementById("toast");
    toast.innerText = msg;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 2000);
}

function showLoading() {
    document.getElementById("loading").style.display = "block";
}
