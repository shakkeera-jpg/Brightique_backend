from django.shortcuts import get_object_or_404
from django.db import transaction

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from order.models import Order
from order.serializers import OrderSerializer

class OrderListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = (
            Order.objects
            .filter(user=request.user)
            .prefetch_related("items")
            .order_by("-created_at")
        )

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class OrderDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        order = get_object_or_404(
            Order.objects.prefetch_related("items"),
            id=pk,
            user=request.user
        )

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CancelOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        with transaction.atomic():
            order = get_object_or_404(
                Order.objects.select_for_update(),
                id=order_id,
                user=request.user
            )

            if order.status == Order.Status.CANCELLED:
                return Response(
                    {"detail": "Order already cancelled"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if order.is_paid:
                return Response(
                    {"detail": "Paid orders cannot be cancelled"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            order.status = Order.Status.CANCELLED
            order.save(update_fields=["status"])

        return Response(
            {
                "success": True,
                "status": order.status
            },
            status=status.HTTP_200_OK
        )
