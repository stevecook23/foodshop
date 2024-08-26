from django.contrib.auth.decorators import login_required
from checkout.models import Order
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserProfileForm

@login_required
def order_history(request):
    profile = request.user.userprofile
    orders = profile.orders.all().order_by('-date')
    
    template = 'profiles/order_history.html'
    context = {
        'orders': orders,
        'on_profile_page': True  # This can be used in the template to highlight the current page in navigation
    }

    return render(request, template, context)

@login_required
def profile(request):
    """ Display the user's profile. """
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Update failed. Please ensure the form is valid.')
    else:
        form = UserProfileForm(instance=profile)
    
    orders = profile.orders.all()

    template = 'profiles/profile.html'
    context = {
        'form': form,
        'orders': orders,
        'on_profile_page': True
    }

    return render(request, template, context)