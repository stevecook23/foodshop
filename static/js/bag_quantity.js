// Add this to your existing JavaScript file or create a new one for the bag page
$(document).ready(function() {
    // Function to handle quantity changes
    function handleQuantityChange(itemId, newQuantity) {
        $.ajax({
            url: `/bag/adjust/${itemId}/`,
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
                'quantity': Math.min(newQuantity, 99)  
            },
            success: function(response) {
                location.reload();
            },
            error: function(xhr, errmsg, err) {
                console.log('Error:', errmsg);
                console.log('XHR:', xhr.responseText);
            }
        });
    }

    // Increment and decrement quantity
    $('.increment-qty, .decrement-qty').click(function(e) {
        e.preventDefault();
        var closestInput = $(this).closest('.input-group').find('.qty_input')[0];
        var currentValue = parseInt($(closestInput).val());
        if ($(this).hasClass('increment-qty')) {
            var newValue = Math.min(currentValue + 1, 99);
        } else {
            var newValue = Math.max(1, currentValue - 1);
        }
        $(closestInput).val(newValue);
        var itemId = $(closestInput).data('item_id');
        handleQuantityChange(itemId, newValue);
    });

    // Handle manual input change
    $('.qty_input').change(function() {
        var itemId = $(this).data('item_id');
        var newValue = parseInt($(this).val());
        if (isNaN(newValue) || newValue < 1) {
            newValue = 1;
        } else if (newValue > 99) {
            newValue = 99;
        }
        $(this).val(newValue);
        handleQuantityChange(itemId, newValue);
    });

    // Update bag when "Update" link is clicked
    $('.update-link').click(function(e) {
        e.preventDefault();
        var itemId = $(this).data('item_id');
        var closestInput = $(this).closest('.row').find('.qty_input');
        var quantity = parseInt(closestInput.val());
        handleQuantityChange(itemId, quantity);
    });

    // Remove item from bag
    $('.remove-item').click(function(e) {
        e.preventDefault();
        var itemId = $(this).data('item_id');
        handleQuantityChange(itemId, 0);
    });

    // Prevent form submission on enter key and trigger change event instead
    $('.qty_input').keypress(function(e) {
        if (e.which === 13) { // Enter key
            e.preventDefault();
            $(this).change();
        }
    });
});