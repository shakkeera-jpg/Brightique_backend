from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import User
from wishlist.serializers import WishlistItemSerializer
from cart.serializers import CartSerializer
from order.serializers import OrderSerializer
from rest_framework.exceptions import AuthenticationFailed



class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'name', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        data = super().validate(attrs)

        if self.user.is_blocked:
            raise AuthenticationFailed(
                "Your account has been blocked by the admin"
            )

        
        data['is_admin'] = self.user.is_staff
        data['name'] = self.user.name
        data['email'] = self.user.email
    
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    wishlist = WishlistItemSerializer(many=True, read_only=True)
    cart = serializers.SerializerMethodField()
    orders = OrderSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "email",
            "wishlist",
            "cart",
            "orders",
        ]

    def get_cart(self, obj):
        try:
            cart = obj.cart
            return CartSerializer(cart).data
        except:
            return None