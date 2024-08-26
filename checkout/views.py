from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from .forms import OrderForm

def checkout(request: HttpRequest) -> HttpResponse:
    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        return redirect(reverse('products'))

    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            # Process the order
            # ...
            return redirect(reverse('checkout_success'))
    else:
        order_form = OrderForm()

    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
    }

    return render(request, template, context)