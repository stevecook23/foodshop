import os
import django
import random
from datetime import timedelta

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodshop.settings")
django.setup()

from django.utils import timezone
from django.contrib.auth.models import User
from products.models import Product, Review

# Sample review data
SAMPLE_REVIEWS = [
    {
        "headline": "Great product!",
        "review_text": "I absolutely love this product. It's exactly what I was looking for and the quality is outstanding."
    },
    {
        "headline": "Good value for money",
        "review_text": "While not perfect, this product offers good value for the price. It does the job well."
    },
    {
        "headline": "Decent, but could be better",
        "review_text": "The product is okay, but there's definitely room for improvement. It meets basic expectations."
    },
    {
        "headline": "Not impressed",
        "review_text": "I expected more from this product. It falls short in several areas and I wouldn't recommend it."
    },
    {
        "headline": "Exceeded expectations",
        "review_text": "This product is even better than I anticipated. The attention to detail is impressive."
    },
    {
        "headline": "Solid choice",
        "review_text": "A reliable product that does what it promises. No complaints here."
    }
]

def create_sample_reviews():
    products = Product.objects.all()
    print(f"Found {products.count()} products")
    
    reviewers = User.objects.filter(username__in=['reviewer1', 'reviewer2', 'reviewer3', 'reviewer4', 'reviewer5'])
    print(f"Found {reviewers.count()} reviewers")

    if not reviewers:
        print("No reviewers found. Please ensure reviewer1 through reviewer5 exist.")
        return

    if not products:
        print("No products found in the database.")
        return

    for product in products:
        print(f"Processing product: {product.name}")
        # Ensure at least 2 reviews per product
        num_reviews = max(2, random.randint(2, 5))
        
        for i in range(num_reviews):
            review_data = random.choice(SAMPLE_REVIEWS)
            reviewer = random.choice(reviewers)
            
            try:
                # Create the review
                review = Review.objects.create(
                    product=product,
                    user=reviewer,
                    headline=review_data['headline'],
                    review_text=review_data['review_text'],
                    created_at=timezone.now() - timedelta(days=random.randint(1, 365))
                )
                print(f"Created review {i+1} for {product.name} by {reviewer.username}")
            except Exception as e:
                print(f"Error creating review for {product.name}: {str(e)}")

if __name__ == "__main__":
    print("Starting sample reviews creation...")
    create_sample_reviews()
    print("Sample reviews creation completed.")