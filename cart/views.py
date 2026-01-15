from django.shortcuts import get_object_or_404
from django.db import transaction

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Cart, CartItem
from .serializers import CartSerializer
from products.models import Product


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)



class AddToCart(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product_id")

        if not product_id:
            return Response(
                {"detail": "Product ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            product = get_object_or_404(
                Product.objects.select_for_update(),
                id=product_id
            )

            cart, _ = Cart.objects.get_or_create(user=request.user)

            item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={"quantity": 1}
            )

            if not created:
                if item.quantity >= product.stock:
                    return Response(
                        {"detail": "Maximum stock reached"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                item.quantity += 1
                item.save(update_fields=["quantity"])

        return Response(
            {"message": "Product added to cart"},
            status=status.HTTP_200_OK
        )


class UpdateCartItem(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        quantity = request.data.get("quantity")

        if quantity is None:
            return Response(
                {"detail": "Quantity is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = int(quantity)
        except ValueError:
            return Response(
                {"detail": "Quantity must be an integer"},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            item = get_object_or_404(
                CartItem.objects.select_for_update(),
                id=pk,
                cart__user=request.user
            )

            if quantity > item.product.stock:
                return Response(
                    {"detail": "Not enough stock"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if quantity <= 0:
                item.delete()
                return Response(
                    {"message": "Product removed from cart"},
                    status=status.HTTP_200_OK
                )

            item.quantity = quantity
            item.save(update_fields=["quantity"])

        return Response(
            {"message": "Quantity updated"},
            status=status.HTTP_200_OK
        )

class RemoveCartItem(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        cart_item = get_object_or_404(
            CartItem,
            id=pk,
            cart__user=request.user
        )

        cart_item.delete()

        return Response(
            {"message": "Product removed from cart"},
            status=status.HTTP_200_OK
        )


