// Ensure all DOM elements are loaded
document.addEventListener('DOMContentLoaded', function() {
    // Attach click events to increment and decrement buttons
    var incrementButton = document.querySelector('.increment-qty');
    var decrementButton = document.querySelector('.decrement-qty');
    var quantityInput = document.querySelector('.qty_input');

    if (incrementButton && decrementButton && quantityInput) {
        incrementButton.addEventListener('click', function(e) {
            e.preventDefault();
            var currentValue = parseInt(quantityInput.value);
            quantityInput.value = currentValue + 1;
        });

        decrementButton.addEventListener('click', function(e) {
            e.preventDefault();
            var currentValue = parseInt(quantityInput.value);
            if (currentValue > 1) {
                quantityInput.value = currentValue - 1;
            }
        });
    }
});