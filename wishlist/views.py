# wishlist/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404

from .models import WishlistItem
from .serializers import WishlistItemSerializer
from products.models import Product


class WishlistView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    
    def get(self, request):
        wishlist = (
            WishlistItem.objects
            .filter(user=request.user)
            .select_related("product")   
        )

        serializer = WishlistItemSerializer(wishlist, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    def post(self, request):
        product_id = request.data.get("product_id")

        if not product_id:
            return Response(
                {"error": "Product ID required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        product = get_object_or_404(Product, id=product_id)

        wishlist_qs = WishlistItem.objects.filter(
            user=request.user,
            product=product
        )

        
        if wishlist_qs.exists():
            wishlist_qs.delete()
            return Response(
                {"removed": True},
                status=status.HTTP_200_OK
            )

        wishlist_item = WishlistItem.objects.create(
            user=request.user,
            product=product
        )

        serializer = WishlistItemSerializer(wishlist_item)
        return Response(
            {"removed": False, "item": serializer.data},
            status=status.HTTP_201_CREATED
        )
