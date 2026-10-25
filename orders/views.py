import uuid
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction

from cart.models import CartItem
from products.models import Product
from .models import Order, OrderItem


@login_required
def checkout(request):
    if request.method == 'POST':
        checkout_token = request.POST.get(
            'checkout_token', ''
        ).strip()

        try:
            checkout_token = str(uuid.UUID(checkout_token))
        except (ValueError, AttributeError):
            return redirect('checkout')
    else:
        checkout_token = str(uuid.uuid4())

    if request.method == 'POST':
        existing_order = Order.objects.filter(
            user=request.user,
            checkout_token=checkout_token
        ).first()

        if existing_order:
            return redirect(
                'order_success',
                order_id=existing_order.id
            )

    items = list(
        CartItem.objects.filter(
            user=request.user
        ).select_related('product')
    )

    if not items:
        return redirect('cart_view')

    total = sum(
        (item.subtotal for item in items),
        Decimal('0.00')
    )

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        pincode = request.POST.get('pincode', '').strip()
        phone = request.POST.get('phone', '').strip()

        if not all([
            full_name, email, address,
            city, state, pincode, phone
        ]):
            return render(request, 'orders/checkout.html', {
                'items': items,
                'total': total,
                'checkout_token': checkout_token,
                'error': 'Please fill in all fields.',
            })

        if not pincode.isdigit() or len(pincode) != 6:
            return render(request, 'orders/checkout.html', {
                'items': items,
                'total': total,
                'checkout_token': checkout_token,
                'error': 'Please enter a valid 6-digit PIN code.',
            })

        with transaction.atomic():
            locked_items = list(
                CartItem.objects.filter(
                    user=request.user
                ).select_related('product').select_for_update()
            )

            if not locked_items:
                return redirect('cart_view')

            product_ids = [item.product_id for item in locked_items]

            locked_products = {
                product.id: product
                for product in Product.objects.filter(
                    id__in=product_ids
                ).select_for_update()
            }

            for item in locked_items:
                product = locked_products.get(item.product_id)

                if product is None or item.quantity > product.stock:
                    available = product.stock if product else 0

                    return render(request, 'orders/checkout.html', {
                        'items': locked_items,
                        'total': sum(
                            (i.subtotal for i in locked_items),
                            Decimal('0.00')
                        ),
                        'checkout_token': checkout_token,
                        'error': (
                            f'Not enough stock for {item.product.name}. '
                            f'Available stock: {available}.'
                        ),
                    })

            total = sum(
                (
                    locked_products[item.product_id].price
                    * item.quantity
                    for item in locked_items
                ),
                Decimal('0.00')
            )

            order = Order.objects.create(
                user=request.user,
                full_name=full_name,
                email=email,
                address=address,
                city=city,
                state=state,
                pincode=pincode,
                phone=phone,
                total_amount=total,
                checkout_token=checkout_token,
            )

            for item in locked_items:
                product = locked_products[item.product_id]

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    price=product.price,
                    quantity=item.quantity,
                )

                product.stock -= item.quantity
                product.save(update_fields=['stock'])

            CartItem.objects.filter(
                user=request.user
            ).delete()

        return redirect('order_success', order_id=order.id)

    return render(request, 'orders/checkout.html', {
        'items': items,
        'total': total,
        'checkout_token': checkout_token,
    })


@login_required
def order_success(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(request, 'orders/order_success.html', {
        'order': order,
    })


@login_required
def order_list(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(request, 'orders/order_list.html', {
        'orders': orders,
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related('items'),
        id=order_id,
        user=request.user
    )

    return render(request, 'orders/order_detail.html', {
        'order': order,
    })