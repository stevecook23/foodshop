function handleQuantityChange(itemId, newQuantity) {
    $.ajax({
        url: `/bag/adjust/${itemId}/`,
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
            'quantity': newQuantity
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

$(document).ready(function() {
    // Increment and decrement quantity
    $('.increment-qty, .decrement-qty').click(function(e) {
        e.preventDefault();
        var closestInput = $(this).closest('.input-group').find('.qty_input')[0];
        var currentValue = parseInt($(closestInput).val());
        if ($(this).hasClass('increment-qty')) {
            var newValue = currentValue + 1;
        } else {
            var newValue = Math.max(1, currentValue - 1);
        }
        $(closestInput).val(newValue);
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

    // Prevent form submission on enter key
    $('.update-form').keypress(function(e) {
        if (e.which === 13) { // Enter key
            e.preventDefault();
            $(this).closest('.row').find('.update-link').click();
        }
    });
});