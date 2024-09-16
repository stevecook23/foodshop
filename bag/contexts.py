"""Contexts for the bag app."""
from decimal import Decimal
from django.conf import settings
from .models import BasketItem
from products.models import Product


def bag_contents(request):
    bag_items = []
    total = 0
    product_count = 0

    if request.user.is_authenticated:
        basket_items = BasketItem.objects.filter(user=request.user)
        for item in basket_items:
            total += item.quantity * item.product.price
            product_count += item.quantity
            bag_items.append({
                'item_id': item.product.id,
                'quantity': item.quantity,
                'product': item.product,
            })
    else:
        bag = request.session.get('bag', {})
        for item_id, quantity in bag.items():
            product = Product.objects.get(id=item_id)
            total += quantity * product.price
            product_count += quantity
            bag_items.append({
                'item_id': item_id,
                'quantity': quantity,
                'product': product,
            })

    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = 0
        free_delivery_delta = 0

    grand_total = delivery + total

    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
    }

    return context
