"""Urls for the products app."""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_products, name='products'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('add/', views.add_product, name='add_product'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('toggle_favourite/<int:product_id>/', views.toggle_favourite, name='toggle_favourite'),
    path('add_review/<int:product_id>/', views.add_review, name='add_review'),
    path('edit_review/<int:review_id>/', views.edit_review, name='edit_review'),
    path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'),
    path('get_review/<int:review_id>/', views.get_review, name='get_review'),
    path('product/<int:product_id>/reviews/', views.all_reviews, name='all_reviews'),
]
