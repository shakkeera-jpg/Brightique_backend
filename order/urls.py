from django.urls import path
from .views import OrderDetailAPIView,OrderListAPIView,CancelOrderAPIView

urlpatterns = [
    path("orders/", OrderListAPIView.as_view()),    
    path("orders/<int:pk>/", OrderDetailAPIView.as_view()),
    path("orders/<int:order_id>/cancel/", CancelOrderAPIView.as_view()),
]