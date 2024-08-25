from django.db import migrations

def migrate_categories(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    for product in Product.objects.all():
        if hasattr(product, 'category') and product.category:
            product.categories.add(product.category)

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_remove_product_category_product_categories'),  # Replace this with your actual last migration
    ]

    operations = [
        migrations.RunPython(migrate_categories),
    ]