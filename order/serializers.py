
from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'name', 'price', 'quantity', 'image']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customerDetails = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "amount",
            "status",
            "payment_method",
            "is_paid",
            "created_at",
            "customerDetails", 
            "items",
        ]
    def get_customerDetails(self, obj):
        return {
            "name": obj.name,
            "phone": obj.phone,
            "email": obj.user.email,
            "street": obj.street,
            "city": obj.city,
            "state": obj.state,
            "zip": obj.zip,
            "country": obj.country,
            "paymentMethod": obj.payment_method,
        }