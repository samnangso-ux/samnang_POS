# sales/admin.py

from django.contrib import admin
from .models import Discount, Product, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ['name', 'category', 'price', 'stock', 'is_active', 'image_preview']
    list_filter   = ['category', 'is_active']
    search_fields = ['name', 'barcode']
    ordering      = ['name']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />'
        return "No image"
    image_preview.short_description = 'Image'
    image_preview.allow_tags = True


class OrderItemInline(admin.TabularInline):
    """បង្ហាញ order items ផ្ទាល់នៅក្នុងទំព័រកែ Order"""
    model  = OrderItem
    extra  = 1    # ចំនួនជួរទទេដែលបង្ហាញសម្រាប់បន្ថែម items ថ្មី
    fields = ['product', 'quantity', 'unit_price']


class DiscountInline(admin.StackedInline):
    """បង្ហាញ discount ផ្ទាល់នៅក្នុងទំព័រកែ Order"""
    model  = Discount
    extra  = 0    # មិនបង្ហាញជួរទទេដែលលាប់លាក់ (OneToOne ទេ ForeignKey)
    fields = ['description', 'amount']

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display  = ['description', 'amount', 'order']
    search_fields = ['description', 'order__pk']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ['pk', 'cashier', 'status', 'created_at']
    list_filter   = ['status']
    search_fields = ['cashier', 'notes']
    ordering      = ['-created_at']
    inlines       = [OrderItemInline, DiscountInline]    # បង្ហាញ items និង discount នៅក្នុងទម្រង់ order

