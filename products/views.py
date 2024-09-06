from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.db.models.functions import Lower
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Favourite
from .forms import ProductForm
from operator import attrgetter
from django.http import JsonResponse

def all_products(request):
    products = Product.objects.all().prefetch_related('categories')
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(categories__name__in=categories).distinct()
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))
            
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
            if sortkey == 'category':
                sortkey = 'categories__name'
            direction = request.GET.get('direction', 'asc')

    # Convert to list to allow Python-based sorting
    products = list(products)

    # Sort the products
    if sort:
        if sort == 'category':
            # Custom sorting for categories
            def category_sort_key(product):
                return sorted(category.name for category in product.categories.all())[0]
            products.sort(key=category_sort_key, reverse=(direction == 'desc'))
        else:
            # General sorting
            products.sort(key=attrgetter(sort), reverse=(direction == 'desc'))

    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    return render(request, 'products/products.html', context)

def product_detail(request, product_id):
    """ A view to show individual product details """
    product = get_object_or_404(Product, pk=product_id)
     # Get related products (from the same category, excluding the current product)
    related_products = Product.objects.filter(categories__in=product.categories.all()).exclude(id=product_id).distinct()[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)

@login_required
def add_product(request):
    """ Add a product to the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()
        
    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)

@login_required
def edit_product(request, product_id):
    """ Edit a product in the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to update product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)

@login_required
def delete_product(request, product_id):
    """ Delete a product from the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect(reverse('products'))

@login_required
def toggle_favourite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    favourite, created = Favourite.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        favourite.delete()
        is_favourite = False
        message = f'{product.name} has been removed from your favourites.'
    else:
        is_favourite = True
        message = f'{product.name} has been added to your favourites.'
    
    return JsonResponse({
        'is_favourite': is_favourite,
        'message': message
    })