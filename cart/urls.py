from django.urls import path
from .views import CartView, AddToCart, UpdateCartItem, RemoveCartItem

urlpatterns = [
    path("cart/", CartView.as_view()),
    path("cart/add/", AddToCart.as_view()),
    path("cart/update/<int:pk>/", UpdateCartItem.as_view()),
    path("cart/remove/<int:pk>/", RemoveCartItem.as_view()),

]