from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator

class Category(models.Model):
    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name

class Product(models.Model):
    categories = models.ManyToManyField('Category', related_name='products', blank=True)
    name = models.CharField(max_length=254)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    sku = models.CharField(max_length=254, null=True, blank=True)
    tags = models.CharField(max_length=254, null=True, blank=True)
    image = models.ImageField(upload_to='product_images', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='product_thumbnails', null=True, blank=True, help_text="Recommended size: 300x300 pixels")

    def __str__(self):
        return self.name
    
class Favourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username}'s favourite: {self.product.name}"
    
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    headline = models.CharField(max_length=200)
    review_text = models.TextField(validators=[MaxLengthValidator(500)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Review for {self.product.name} by {self.user.username}'