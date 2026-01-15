from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.db import transaction

import razorpay
import logging
from cart.models import Cart
from order.models import Order, OrderItem
from order.serializers import OrderSerializer

logger = logging.getLogger(__name__)

client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


def finalize_order(order, user):
    cart = Cart.objects.select_for_update().get(user=user)
    cart_items = cart.items.all()

    if order.items.exists():
        return

    for item in cart_items:
        product = item.product

        if product.stock < item.quantity:
            raise Exception(f"Insufficient stock for {product.name}")

        OrderItem.objects.create(
            order=order,
            product=product,
            name=product.name,
            price=product.price,
            quantity=item.quantity,
            image=product.image
        )

        product.stock -= item.quantity
        product.save()

    
    cart.items.all().delete()


class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")
        payment_method = request.data.get("payment_method")

        if not amount or payment_method not in ["cod", "razorpay"]:
            return Response(
                {"error": "Amount and valid payment method required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        amount = int(amount)
        amount_paise = amount * 100

        
        if payment_method == "cod":
            order = Order.objects.create(
                user=request.user,
                amount=amount_paise,
                is_paid=False,
                status="pending",
                payment_method="cod",

                name=request.data["name"],
                phone=request.data["phone"],
                street=request.data["street"],
                city=request.data["city"],
                state=request.data["state"],
                zip=request.data["zip"],
                country=request.data["country"],
            )

            return Response({
                "success": True,
                "order_id": order.id,
                "payment_method": "cod"
            })

        
        try:
            razorpay_order = client.order.create({
                "amount": amount_paise,
                "currency": "INR",
                "payment_capture": 1
            })

            return Response({
                "razorpay_order_id": razorpay_order["id"],
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "amount": amount_paise,
                "address": request.data  
            })

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ConfirmCODAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, order_id):
        try:
            order = Order.objects.select_for_update().get(
                id=order_id,
                user=request.user
            )

            finalize_order(order, request.user)

            return Response({
                "success": True,
                "order_id": order.id
            })

        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )



class VerifyRazorpayPaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        data = request.data

        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_signature = data.get("razorpay_signature")

        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return Response(
                {"error": "Missing payment fields"},
                status=status.HTTP_400_BAD_REQUEST
            )

        
        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature
            })
        except Exception:
            return Response(
                {"error": "Payment verification failed"},
                status=status.HTTP_400_BAD_REQUEST
            )

       
        order = Order.objects.create(
            user=request.user,
            amount=data["amount"],
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_id=razorpay_payment_id,
            is_paid=True,
            status="confirmed",
            payment_method="razorpay",

            name=data["name"],
            phone=data["phone"],
            street=data["street"],
            city=data["city"],
            state=data["state"],
            zip=data["zip"],
            country=data["country"],
        )

        finalize_order(order, request.user)

        return Response({
            "success": True,
            "order_id": order.id
        })
