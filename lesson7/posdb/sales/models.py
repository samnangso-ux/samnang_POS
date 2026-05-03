# sales/models.py

from django.db import models
from decimal import Decimal


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('food',        'អាហារ និងភេសជ្ជៈ'),
        ('electronics', 'អេឡិចត្រូនិក'),
        ('clothing',    'សម្លៀកបំពាក់'),
        ('household',   'គ្រឿងសង្ហារឹម'),
        ('other',       'ផ្សេងៗ'),
    ]

    name       = models.CharField(max_length=200)
    category   = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price      = models.DecimalField(max_digits=8, decimal_places=2)   # ឧ. 12.99
    stock      = models.PositiveIntegerField(default=0)                # ចំនួនក្នុងស្តុក
    barcode    = models.CharField(max_length=50, unique=True, blank=True)
    image      = models.ImageField(upload_to='products/', blank=True, null=True)  # Product image
    is_active  = models.BooleanField(default=True)                     # លាក់ទំនិញឈប់លក់

    def __str__(self):
        return f"{self.name}  —  ${self.price}  (ស្តុក: {self.stock})"

    class Meta:
        ordering = ['name']



class Order(models.Model):
    STATUS_CHOICES = [
        ('open',       'បានបើក'),
        ('paid',       'បានបង់'),
        ('refunded',   'បានសង'),
        ('cancelled',  'បានលុបចោល'),
    ]

    cashier    = models.CharField(max_length=100)           # ឈ្មោះ ឬ ID បុគ្គលិក
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)    # កំណត់ពេលបង្កើតការបញ្ជាទិញ
    notes      = models.TextField(blank=True)

    @property
    def total(self):
        subtotal = sum(item.subtotal for item in self.items.all())
        try:
            return float(subtotal) - float(self.discount.amount) #make sure to convert to float for accurate calculation
        except Discount.DoesNotExist:
            return float(subtotal) #make sure to convert to float for consistent return type

    def __str__(self):
        return f"ការបញ្ជាទិញ #{self.pk}  [{self.status.upper()}]  —  ${self.total:.2f}"

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    order      = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product    = models.ForeignKey(Product, on_delete=models.PROTECT)   # PROTECT ការពារការលុបផលិតផលដែលមានការលក់
    quantity   = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)    # តម្លៃនៅពេលលក់

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.quantity} × {self.product.name}  @  ${self.unit_price}"
    
class Discount(models.Model):
    order       = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='discount')
    description = models.CharField(max_length=200)   # ឧ. "ការបញ្ចុះតម្លៃបុគ្គលិក"
    amount      = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.description} (—${self.amount}) នៅការបញ្ជាទិញ #{self.order.pk}"
    
