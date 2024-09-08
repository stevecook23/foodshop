"""This module contains views for the foodshop application."""

from django.http import HttpResponse

def home(request):
    """View function for the home page of the site."""
    return HttpResponse("Welcome to FoodShop!")
