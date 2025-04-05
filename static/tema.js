document.addEventListener("DOMContentLoaded", function () {
    const botaoTema = document.getElementById("botao-tema");

    if (localStorage.getItem("tema") === "escuro") {
        document.body.classList.add("dark-mode");
    }

    botaoTema.addEventListener("click", () => {
        document.body.classList.toggle("dark-mode");
        if (document.body.classList.contains("dark-mode")) {
            localStorage.setItem("tema", "escuro");
        } else {
            localStorage.setItem("tema", "claro");
        }
    });
});
