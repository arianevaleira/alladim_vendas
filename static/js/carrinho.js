document.addEventListener("DOMContentLoaded", function () {
    let modal = document.getElementById("confirmModal");
    let confirmButton = document.getElementById("confirmRemove");
    let cancelButton = document.getElementById("cancelRemove");
    let itemIdToRemove = null; 


    document.querySelectorAll(".btn-decrement").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            let form = this.closest("form");
            let quantidadeElement = form.querySelector(".quantidade");
            let quantidade = parseInt(quantidadeElement.innerText);
            let itemId = this.getAttribute("data-item-id");

            if (quantidade === 1) { 
                itemIdToRemove = itemId;
                modal.style.display = "flex"; 
            } else {
                fetch(`/alterar_quantidade/${itemId}/decrement`, { method: "POST" })
                    .then(() => location.reload());
            }
        });
    });

    // Quando clicar em "Sim", remove o item
    confirmButton.addEventListener("click", function () {
        if (itemIdToRemove) {
            fetch(`/remover_do_carrinho/${itemIdToRemove}`, { method: "POST" })
                .then(() => location.reload());
        }
    });

    // Quando clicar em "Cancelar", esconde o modal
    cancelButton.addEventListener("click", function () {
        modal.style.display = "none";
        itemIdToRemove = null;
    });
});
