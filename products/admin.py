from django.contrib import admin
from .models import Product, Category

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('friendly_name', 'name')
    search_fields = ['name', 'friendly_name']

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'rating', 'sku')
    list_filter = ('category', 'rating')
    search_fields = ['name', 'description', 'sku']
    ordering = ('sku',)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)