"""Views for the shopping bag app"""
from decimal import Decimal
from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.template.loader import render_to_string
from products.models import Product


def view_bag(request):
    """ A view that renders the bag contents page """
    return render(request, 'bag/bag.html')


def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to the shopping bag """
    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')
    bag = request.session.get('bag', {})

    if item_id in list(bag.keys()):
        bag[item_id] += quantity
        messages.success(request, f'Updated {product.name} quantity to {bag[item_id]}')
    else:
        bag[item_id] = quantity
        messages.success(request, f'Added {product.name} to your bag')

    request.session['bag'] = bag
    return redirect(redirect_url)


def adjust_bag(request, item_id):
    """Adjust the quantity of the specified product to the specified amount"""
    try:
        product = get_object_or_404(Product, pk=item_id)
        quantity = int(request.POST.get('quantity', 0))
        bag = request.session.get('bag', {})

        if quantity > 0:
            bag[item_id] = quantity
            messages.info(request, f'Updated {product.name} quantity to {bag[item_id]}')
        else:
            bag.pop(item_id, None)
            messages.info(request, f'Removed {product.name} from your bag')

        request.session['bag'] = bag

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(get_bag_data(request))
        return redirect(reverse('view_bag'))

    except Exception as e:
        messages.error(request, f'Error updating bag: {str(e)}')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=400)
        return redirect(reverse('view_bag'))


def remove_from_bag(request, item_id):
    """Remove the item from the shopping bag"""
    try:
        product = get_object_or_404(Product, pk=item_id)
        bag = request.session.get('bag', {})

        if item_id in bag:
            bag.pop(item_id)
            request.session['bag'] = bag
            messages.success(request, f'Removed {product.name} from your bag')
        else:
            messages.error(request, f'Error removing item: {product.name} was not in your bag')

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(get_bag_data(request))
        return HttpResponse(status=200)

    except Exception as e:
        messages.error(request, f'Error removing item: {str(e)}')
        return JsonResponse({'error': str(e)}, status=500)


def get_bag_data(request):
    bag_items = []
    total = 0
    product_count = 0
    bag = request.session.get('bag', {})

    for item_id, item_data in bag.items():
        product = get_object_or_404(Product, pk=item_id)
        total += item_data * product.price
        product_count += item_data
        bag_items.append({
            'item_id': item_id,
            'quantity': item_data,
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

    return {
        'bag_items': render_to_string('bag/bag_contents.html', context, request=request),
        'total': total,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'grand_total': grand_total,
        'product_count': product_count,
    }
