import uuid
from django.db import models
from django.db.models import Sum
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from products.models import Product


class Order(models.Model):
    order_number = models.CharField(max_length=32, unique=True, editable=False)
    full_name = models.CharField(_('Full Name'), max_length=50)
    email = models.EmailField(_('Email Address'))
    phone_number = models.CharField(_('Phone Number'), max_length=20)
    country = models.CharField(_('Country'), max_length=40)
    postcode = models.CharField(_('Postcode'), max_length=20, blank=True, null=True)
    town_or_city = models.CharField(_('Town or City'), max_length=40)
    street_address1 = models.CharField(_('Street Address 1'), max_length=80)
    street_address2 = models.CharField(_('Street Address 2'), max_length=80, blank=True, null=True)
    county = models.CharField(_('County'), max_length=80, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    delivery_cost = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=0, 
        validators=[MinValueValidator(0)]
    )
    order_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        validators=[MinValueValidator(0)]
    )
    grand_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        validators=[MinValueValidator(0)]
    )

    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID
        """
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """
        Update grand total each time a line item is added,
        accounting for delivery costs.
        """
        self.order_total = self.lineitems.aggregate(Sum('lineitem_total'))['lineitem_total__sum'] or 0
        if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = self.order_total * settings.STANDARD_DELIVERY_PERCENTAGE / 100
        else:
            self.delivery_cost = 0
        self.grand_total = self.order_total + self.delivery_cost
        self.save()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_number}"

    class Meta:
        ordering = ['-date']


class OrderLineItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='lineitems')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_size = models.CharField(max_length=2, blank=True, null=True)  # XS, S, M, L, XL
    quantity = models.PositiveIntegerField(default=0)
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem total
        and update the order total.
        """
        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)
        self.order.update_total()

    def __str__(self):
        return f'SKU {self.product.sku} on order {self.order.order_number}'

    class Meta:
        verbose_name = 'Order Line Item'
        verbose_name_plural = 'Order Line Items'