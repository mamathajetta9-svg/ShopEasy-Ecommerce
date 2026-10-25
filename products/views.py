

from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Wishlist
from django.shortcuts import render, get_object_or_404, redirect


def get_image_urls():
    return {
        "Wireless Headphones": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=500&q=80",
        "Smart Watch": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=500&q=80",
        "Bluetooth Speaker": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=500&q=80",
        "Wireless Mouse": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=500&q=80",
        "Mechanical Keyboard": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=500&q=80",
        "Smartphone": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=500&q=80",
        "Power Bank": "https://images.philips.com/is/image/philipsconsumer/tpv_73365?$png$&wid=410&hei=410&fit=constrain",
        "Casual Sneakers": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=500&q=80",
        "Travel Backpack": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=500&q=80",
        "USB Flash Drive": "https://images.unsplash.com/photo-1531492746076-161ca9bcad58?auto=format&fit=crop&w=500&q=80",
    }


def add_display_images(products):
    image_urls = get_image_urls()

    for product in products:
        if product.image:
            product.display_image_url = product.image.url
        else:
            product.display_image_url = image_urls.get(
                product.name, ""
            )

    return products


def home(request):
    products = Product.objects.all().order_by('-created_at')

    search_query = request.GET.get('q', '').strip()
    selected_category = request.GET.get('category', '').strip()

    # Search by product name or description
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Filter by selected category
    if selected_category:
        products = products.filter(category=selected_category)

    # Add image URLs for display
    products = add_display_images(products)

    # Get unique categories for dropdown
    categories = Product.objects.order_by(
        'category'
    ).values_list(
        'category', flat=True
    ).distinct()

    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': selected_category,
    }

    return render(request, 'products/home.html', context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    add_display_images([product])

    return render(request, 'products/detail.html', {
        'product': product,
    })



@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related('product')

    return render(request, 'products/wishlist.html', {
        'wishlist_items': wishlist_items,
    })


@login_required
@require_POST
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product,
    )

    messages.success(request, 'Product added to your wishlist!')
    return redirect(request.POST.get('next') or 'wishlist')


@login_required
@require_POST
def remove_from_wishlist(request, product_id):
    Wishlist.objects.filter(
        user=request.user,
        product_id=product_id,
    ).delete()

    messages.success(request, 'Product removed from your wishlist!')
    return redirect('wishlist')


