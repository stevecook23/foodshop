document.addEventListener('DOMContentLoaded', function() {
    // Attach click events to increment and decrement buttons
    var incrementButton = document.querySelector('.increment-qty');
    var decrementButton = document.querySelector('.decrement-qty');
    var quantityInput = document.querySelector('.qty_input');

    if (incrementButton && decrementButton && quantityInput) {
        incrementButton.addEventListener('click', function(e) {
            e.preventDefault();
            var currentValue = parseInt(quantityInput.value);
            quantityInput.value = Math.min(currentValue + 1, 99);
        });

        decrementButton.addEventListener('click', function(e) {
            e.preventDefault();
            var currentValue = parseInt(quantityInput.value);
            if (currentValue > 1) {
                quantityInput.value = currentValue - 1;
            }
        });

        quantityInput.addEventListener('change', function() {
            var value = parseInt(this.value);
            if (isNaN(value) || value < 1) {
                this.value = 1;
            } else if (value > 99) {
                this.value = 99;
            }
        });
    }
});