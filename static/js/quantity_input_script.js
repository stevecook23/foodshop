function handleQuantityChange(itemId, newQuantity) {
    $.ajax({
        url: `/bag/adjust/${itemId}/`,
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
            'quantity': newQuantity
        },
        success: function(response) {
            updateBag(response);
        },
        error: function(xhr, errmsg, err) {
            console.log(errmsg);
        }
    });
}

function removeItem(itemId) {
    $.ajax({
        url: `/bag/remove/${itemId}/`,
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
        },
        success: function(response) {
            updateBag(response);
        },
        error: function(xhr, errmsg, err) {
            console.log(errmsg);
        }
    });
}

function updateBag(response) {
    $('.bag-contents').html(response.bag_items);
    
    // Parse the values as floats and use toFixed(2) to ensure 2 decimal places
    $('#bag-total').text(parseFloat(response.total).toFixed(2));
    $('#delivery-cost').text(parseFloat(response.delivery).toFixed(2));
    $('#grand-total').text(parseFloat(response.grand_total).toFixed(2));
    
    // Update the top-right bag total
    $('.bag-total-link p').text('£' + parseFloat(response.grand_total).toFixed(2));

    if (parseFloat(response.free_delivery_delta) > 0) {
        $('#free-delivery-delta').text(parseFloat(response.free_delivery_delta).toFixed(2));
        $('.free-delivery-warning').show();
    } else {
        $('.free-delivery-warning').hide();
    }

    if (response.product_count === 0) {
        location.reload();
    }
}

$(document).ready(function() {
    // Use event delegation for dynamically added elements
    $(document).on('click', '.increment-qty, .decrement-qty', function(e) {
        e.preventDefault();
        var itemId = $(this).data('item_id');
        var closestInput = $(this).closest('.input-group').find('.qty_input')[0];
        var currentValue = parseInt($(closestInput).val());
        if ($(this).hasClass('increment-qty')) {
            var newValue = currentValue + 1;
        } else {
            var newValue = Math.max(1, currentValue - 1);
        }
        $(closestInput).val(newValue);
        handleQuantityChange(itemId, newValue);
    });

    $(document).on('change', '.qty_input', function() {
        var itemId = $(this).data('item_id');
        var newValue = $(this).val();
        handleQuantityChange(itemId, newValue);
    });

    $(document).on('click', '.remove-item', function(e) {
        e.preventDefault();
        var $this = $(this);
        var productId = $this.data('product_id');
        var itemId = $this.attr('id').split('_')[1];
        
        console.log('Product ID from data attribute:', productId);
        console.log('Item ID from element ID:', itemId);
        console.log('All data attributes:', $this.data());
        
        if (productId) {
            removeItem(productId);
        } else if (itemId) {
            removeItem(itemId);
        } else {
            console.error('Neither Product ID nor Item ID could be found');
        }
    });
});

function removeItem(id) {
    console.log('Attempting to remove item with ID:', id);
    $.ajax({
        url: `/bag/remove/${id}/`,
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
        },
        success: function(response) {
            console.log('Item removed successfully');
            updateBag(response);
        },
        error: function(xhr, errmsg, err) {
            console.error('Error:', errmsg);
            console.error('XHR:', xhr.responseText);
            console.error('Error object:', err);
        }
    });
}