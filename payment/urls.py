from django.urls import path
from .views import CreateOrderAPIView, VerifyRazorpayPaymentAPIView,ConfirmCODAPIView

urlpatterns = [
    path("create-order/", CreateOrderAPIView.as_view(), name="create_order"),
    path("confirm-cod/<int:order_id>/", ConfirmCODAPIView.as_view()),  
    path("verify-payment/", VerifyRazorpayPaymentAPIView.as_view(), name="verify_payment"),
]
