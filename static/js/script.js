function validateForm() {
    const fileInput = document.querySelector('input[name="file"]');
    const textInput = document.querySelector('textarea[name="text"]');
    if (!fileInput.value && !textInput.value.trim()) {
        alert("Por favor, envie um arquivo ou insira um texto.");
        return false;
    }
    return true;
}

const copyBtn = document.getElementById("copy-btn");
if (copyBtn) {
    copyBtn.addEventListener("click", () => {
        const suggestion = document.getElementById("suggestion-text").innerText.trim();
        if (!suggestion) {
            alert("Não há resposta para copiar.");
            return;
        }

        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(suggestion)
                .then(() => alert("Resposta copiada para a área de transferência!"))
                .catch(err => {
                    console.error("Erro ao copiar:", err);
                    alert("Não foi possível copiar a resposta.");
                });
        } else {
            const textarea = document.createElement("textarea");
            textarea.value = suggestion;
            textarea.style.position = "fixed";
            textarea.style.left = "-9999px";
            document.body.appendChild(textarea);
            textarea.focus();
            textarea.select();

            try {
                document.execCommand("copy");
                alert("Resposta copiada para a área de transferência!");
            } catch (err) {
                console.error("Erro ao copiar:", err);
                alert("Não foi possível copiar a resposta.");
            }

            document.body.removeChild(textarea);
        }
    });
}
