from products.views import add_display_images
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages

from products.models import Product
from .models import CartItem


@login_required
def cart_view(request):
    items = CartItem.objects.filter(
        user=request.user
    ).select_related('product')
    add_display_images([item.product for item in items])

    total = sum(item.subtotal for item in items)
    

    return render(request, 'cart/cart.html', {
        'items': items,
        'total': total,
    })


@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.stock < 1:
        messages.error(request, 'Product is out of stock.')
        return redirect('home')

    item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1},
    )

    if not created:
        if item.quantity < product.stock:
            item.quantity += 1
            item.save(update_fields=['quantity'])
        else:
            messages.warning(
                request,
                'Available stock limit reached.'
            )
            return redirect('cart_view')

    messages.success(request, 'Product added to cart!')
    return redirect('cart_view')


@login_required
@require_POST
def increase_quantity(request, item_id):
    item = get_object_or_404(
        CartItem.objects.select_related('product'),
        id=item_id,
        user=request.user,
    )

    if item.quantity < item.product.stock:
        item.quantity += 1
        item.save(update_fields=['quantity'])
    else:
        messages.warning(
            request,
            'You cannot add more than available stock.'
        )

    return redirect('cart_view')


@login_required
@require_POST
def decrease_quantity(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        user=request.user,
    )

    if item.quantity > 1:
        item.quantity -= 1
        item.save(update_fields=['quantity'])
    else:
        messages.info(
            request,
            'Quantity cannot be less than 1. Remove the item if needed.'
        )

    return redirect('cart_view')


@login_required
@require_POST
def remove_from_cart(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        user=request.user,
    )

    item.delete()
    messages.success(request, 'Product removed from cart.')

    return redirect('cart_view')
