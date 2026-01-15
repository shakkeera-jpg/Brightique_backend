from django.db import models
from django.conf import settings
from products.models import Product

class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    amount = models.IntegerField()  # paise
    is_paid = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    
    name = models.CharField(max_length=100,blank=True)
    phone = models.CharField(max_length=15, blank=True)
    street = models.CharField(max_length=255,blank=True)
    city = models.CharField(max_length=100,blank=True)
    state = models.CharField(max_length=100,blank=True)
    zip = models.CharField(max_length=20,blank=True)
    country = models.CharField(max_length=100,blank=True)

    payment_method = models.CharField(max_length=20,default="method")

    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    razorpay_signature = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.user}"




class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="items",  
        on_delete=models.CASCADE
    )
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.IntegerField()   
    quantity = models.IntegerField()
    image = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} x {self.quantity}"
