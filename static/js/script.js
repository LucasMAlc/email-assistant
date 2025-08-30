function validateForm() {
    const fileInput = document.querySelector('input[name="file"]');
    const textInput = document.querySelector('textarea[name="text"]');
    if (!fileInput.value && !textInput.value.trim()) {
        alert("Por favor, envie um arquivo ou insira um texto.");
        return false;
    }
    return true;
}

function downloadResponse(categoria, confianca, fonte, resposta) {
    const content = `Categoria: ${categoria}\nConfiança: ${confianca}\nFonte: ${fonte}\n\nResposta sugerida:\n${resposta}`;
    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "resposta_email.txt";
    link.click();
}
