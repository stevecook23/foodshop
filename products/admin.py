"""Admin for the products app."""
from django.contrib import admin
from .models import Product, Category


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('friendly_name', 'name')
    search_fields = ['name', 'friendly_name']


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_categories', 'price', 'rating', 'sku', 'tags', 'thumbnail')
    list_filter = ('categories', 'rating')
    search_fields = ['name', 'description', 'sku', 'tags']
    ordering = ('sku',)
    filter_horizontal = ('categories',)
    fields = (
        'name',
        'categories',
        'description',
        'price',
        'rating',
        'image',
        'thumbnail',
        'sku',
        'tags'
    )

    def get_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])
    get_categories.short_description = 'Categories'


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
