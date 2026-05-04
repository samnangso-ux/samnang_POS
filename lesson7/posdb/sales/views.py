# sales/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from .models import Product, Order, OrderItem, Discount
from .form import OrderItemForm
from .checkout_form import CheckoutForm

def product_list(request):
    """បង្ហាញផលិតផល active ទាំងអស់ តម្រៀប A–Z"""
    products = Product.objects.filter(is_active=True)
    return render(request, 'sales/product_list.html', {'products': products})


def product_detail(request, pk):
    """បង្ហាញព័ត៌មានលម្អិតសម្រាប់ផលិតផលតែមួយ។ Return 404 ប្រសិនបើរកមិនឃើញ"""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'sales/product_detail.html', {'product': product})


def order_list(request):
    """បង្ហាញការបញ្ជាទិញទាំងអស់ ថ្មីបំផុតមុន"""
    orders = Order.objects.all()
    return render(request, 'sales/order_list.html', {'orders': orders})


#@login_required
def create_order(request):
    """Instantly create an open order and jump straight to the add-items page."""
    # Handle case when user is not logged in
    cashier = request.user if request.user.is_authenticated else "Anonymous"
    
    order = Order.objects.create(
        cashier=cashier,
        status='open',
    )
    return redirect('add_item', pk=order.pk)


#@login_required #only login can open webpage
def add_item(request, pk):
    """
    Let the cashier add line items to an open order, then proceed to checkout.
    """
    order = get_object_or_404(Order, pk=pk) 

    if request.method == 'POST': # post when user submit info
        # "Proceed to Checkout" button - mark as paid immediately
        if 'proceed_checkout' in request.POST:
            if not order.items.exists():
                messages.error(request, "Cannot checkout with an empty order. Add items first.")
                return redirect('add_item', pk=order.pk)
            
            # Mark order as paid immediately
            order.status = 'paid'
            order.save()
            messages.success(request, f"✓ Order #{order.pk} completed! Total: ${order.total:.2f}")
            return redirect('order_list')

        # Add a line item
        item_form = OrderItemForm(request.POST)
        if item_form.is_valid():
            item = item_form.save(commit=False) #save object but not yet commit
            item.order = order
            item.unit_price = item.product.price   # snapshot the current price
            product = item.product
            if item.quantity > product.stock:
                messages.error(request, f"Cannot add {product.name}: only {product.stock} left in stock.")
                return redirect('add_item', pk=order.pk)
            product.stock -= item.quantity
            product.save()
            item.save()
            messages.success(request, f"✓ Added {item.product.name} to order")
            return redirect('add_item', pk=order.pk)
    else:
        item_form = OrderItemForm() #return item form (ទទេ)

    return render(request, 'sales/add_item.html', {
        'order':     order,
        'item_form': item_form,
        'items':     order.items.select_related('product'),
    })
#@login_required
def checkout(request, pk):
    """
    Complete checkout: apply discounts, select payment method, and finalize order.
    """
    order = get_object_or_404(Order, pk=pk)
    items = order.items.select_related('product')

    # Calculate subtotal
    subtotal = sum(item.subtotal for item in items) if items else Decimal('0.00')

    if request.method == 'POST':
        # Handle item removal
        if 'remove_item' in request.POST:
            item_id = request.POST.get('remove_item')
            try:
                item = OrderItem.objects.get(pk=item_id, order=order)
                product = item.product
                product.stock += item.quantity
                product.save()
                product_name = product.name
                item.delete()
                messages.success(request, f"✓ Removed {product_name} from order")
                return redirect('checkout', pk=order.pk)
            except OrderItem.DoesNotExist:
                messages.error(request, "Item not found")
                return redirect('checkout', pk=order.pk)

        # Handle checkout completion
        if 'complete_checkout' in request.POST:
            checkout_form = CheckoutForm(request.POST)
            
            if not items:
                messages.error(request, "Cannot checkout with an empty order.")
                return redirect('add_item', pk=order.pk)

            if checkout_form.is_valid():
                # Apply discount if selected
                discount_type = checkout_form.cleaned_data.get('discount_type')
                
                # Remove existing discount if any
                if order.discount:
                    order.discount.delete()

                if discount_type == 'staff':
                    # 10% staff discount
                    discount_amount = subtotal * Decimal('0.10')
                    Discount.objects.create(
                        order=order,
                        description='Staff Discount (10%)',
                        amount=discount_amount
                    )
                    messages.success(request, f"✓ Applied 10% staff discount: -${discount_amount:.2f}")
                
                elif discount_type == 'loyalty':
                    # 5% loyalty discount
                    discount_amount = subtotal * Decimal('0.05')
                    Discount.objects.create(
                        order=order,
                        description='Loyalty Discount (5%)',
                        amount=discount_amount
                    )
                    messages.success(request, f"✓ Applied 5% loyalty discount: -${discount_amount:.2f}")
                
                elif discount_type == 'custom':
                    # Custom discount
                    custom_amount = checkout_form.cleaned_data.get('custom_amount')
                    if custom_amount and custom_amount > 0:
                        if custom_amount > subtotal:
                            messages.error(request, "Discount cannot exceed subtotal")
                        else:
                            Discount.objects.create(
                                order=order,
                                description='Custom Discount',
                                amount=custom_amount
                            )
                            messages.success(request, f"✓ Applied custom discount: -${custom_amount:.2f}")

                # Add order notes if provided
                notes = checkout_form.cleaned_data.get('notes', '').strip()
                if notes:
                    order.notes = notes
                
                # Mark order as paid
                order.status = 'paid'
                order.save()

                # Get payment method for confirmation
                payment_method = checkout_form.cleaned_data.get('payment_method', 'cash')
                method_display = dict(checkout_form.fields['payment_method'].choices).get(payment_method, 'Unknown')
                
                messages.success(request, f"✓ Order completed! Payment received via {method_display}")
                return redirect('order_list')
            else:
                messages.error(request, "Please fix the errors in the form")
        
        # Initial form if not processing
        checkout_form = CheckoutForm()
    else:
        checkout_form = CheckoutForm()

    return render(request, 'sales/checkout.html', {
        'order': order,
        'items': items,
        'subtotal': subtotal,
        'checkout_form': checkout_form,
    })
