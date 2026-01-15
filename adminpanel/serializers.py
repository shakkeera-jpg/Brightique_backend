from rest_framework import serializers
from users.models import User
from products.models import Product

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "email",
            "role",
            "is_blocked",
            "created_at",
            "last_login",
        ]
        read_only_fields = [
            "id",
            "name",
            "email",
            "role",
            "created_at",
            "last_login",
        ]


class AdminProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"