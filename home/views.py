"""Views for the home app"""
from django.shortcuts import render

def home(request):
    return render(request, 'home/index.html')
