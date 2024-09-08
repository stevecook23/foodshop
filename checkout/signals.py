"""Used for updating the order total when a line item is created, updated or deleted."""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import OrderLineItem


@receiver(post_save, sender=OrderLineItem)
def update_on_save(sender, instance, created, **kwargs):
    """
    Update order total on lineitem update/create
    """
    with transaction.atomic():
        instance.order.update_total()


@receiver(post_delete, sender=OrderLineItem)
def update_on_delete(sender, instance, **kwargs):
    """
    Update order total on lineitem delete
    """
    with transaction.atomic():
        instance.order.update_total()
