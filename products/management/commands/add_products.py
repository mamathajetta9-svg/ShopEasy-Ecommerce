
from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = "Add sample products to the store"

    def handle(self, *args, **options):
        products = [
            {
                "name": "Wireless Headphones",
                "category": "Electronics",
                "price": "1499.00",
                "stock": 20,
                "description": "Wireless headphones with clear sound.",
            },
            {
                "name": "Smart Watch",
                "category": "Electronics",
                "price": "2499.00",
                "stock": 15,
                "description": "Smart watch for everyday use.",
            },
            {
                "name": "Bluetooth Speaker",
                "category": "Electronics",
                "price": "1299.00",
                "stock": 18,
                "description": "Portable Bluetooth speaker.",
            },
            {
                "name": "Wireless Mouse",
                "category": "Accessories",
                "price": "599.00",
                "stock": 30,
                "description": "Wireless mouse for work and study.",
            },
            {
                "name": "Mechanical Keyboard",
                "category": "Accessories",
                "price": "1899.00",
                "stock": 12,
                "description": "Keyboard for everyday computing.",
            },
            {
                "name": "Smartphone",
                "category": "Mobiles",
                "price": "14999.00",
                "stock": 10,
                "description": "Smartphone for everyday use.",
            },
            {
                "name": "Power Bank",
                "category": "Accessories",
                "price": "999.00",
                "stock": 25,
                "description": "Portable power bank.",
            },
            {
                "name": "Casual Sneakers",
                "category": "Fashion",
                "price": "1799.00",
                "stock": 14,
                "description": "Comfortable casual sneakers.",
            },
            {
                "name": "Travel Backpack",
                "category": "Fashion",
                "price": "1199.00",
                "stock": 16,
                "description": "Backpack for daily use and travel.",
            },
            {
                "name": "USB Flash Drive",
                "category": "Accessories",
                "price": "449.00",
                "stock": 35,
                "description": "USB storage drive for files.",
            },
        ]

        added = 0

        for item in products:
            product, created = Product.objects.get_or_create(
                name=item["name"],
                defaults=item,
            )
            if created:
                added += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Added {added} new products. Total products: {Product.objects.count()}"
            )
        )
