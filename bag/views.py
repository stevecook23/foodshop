"""Views for the shopping bag app"""
from decimal import Decimal
from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.template.loader import render_to_string
from products.models import Product
from django.contrib.auth.decorators import login_required
from .models import BasketItem


def view_bag(request):
    """ A view that renders the bag contents page """
    return render(request, 'bag/bag.html')


@login_required
def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to the shopping bag """
    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')

    basket_item, created = BasketItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        basket_item.quantity += quantity
        basket_item.save()

    messages.success(request, f'Added {product.name} to your bag')
    return redirect(redirect_url)


@login_required
def adjust_bag(request, item_id):
    """Adjust the quantity of the specified product to the specified amount"""
    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get('quantity'))
    
    basket_item = BasketItem.objects.filter(user=request.user, product=product).first()
    
    if basket_item:
        if quantity > 0:
            basket_item.quantity = quantity
            basket_item.save()
        else:
            basket_item.delete()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(get_bag_data(request))
    return redirect(reverse('view_bag'))


@login_required
def remove_from_bag(request, item_id):
    """Remove the item from the shopping bag"""
    try:
        product = get_object_or_404(Product, pk=item_id)
        BasketItem.objects.filter(user=request.user, product=product).delete()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(get_bag_data(request))
        return HttpResponse(status=200)

    except Exception as e:
        messages.error(request, f'Error removing item: {str(e)}')
        return JsonResponse({'error': str(e)}, status=500)

def get_bag_data(request):
    basket_items = BasketItem.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in basket_items)
    product_count = sum(item.quantity for item in basket_items)

    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = 0
        free_delivery_delta = 0
    
    grand_total = delivery + total
    
    context = {
        'bag_items': basket_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
    }

    return {
        'bag_items': render_to_string('bag/bag_contents.html', context, request=request),
        'total': total,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'grand_total': grand_total,
        'product_count': product_count,
    }
