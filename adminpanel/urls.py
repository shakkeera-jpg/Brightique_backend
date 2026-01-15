from django.urls import path
from .views import AdminDashboardView
from .views import AdminUserListView, AdminUserDetailView,AdminProductListCreateView,AdminProductDetailView,AdminCategoryListView,AdminOrderListAPIView,AdminOrderStatusUpdateAPIView,AdminOrderOverviewAPIView,AdminSendNotificationAPIView

urlpatterns = [
    path("dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("users/", AdminUserListView.as_view()),
    path("users/<int:pk>/", AdminUserDetailView.as_view()),
    path("admin/products/", AdminProductListCreateView.as_view()),
    path("admin/products/<int:pk>/", AdminProductDetailView.as_view()),
    path("admin/categories/", AdminCategoryListView.as_view(), name="admin-categories"),
    path("admin/orders/", AdminOrderListAPIView.as_view(), name="admin-orders"),
    path("admin/orders/<int:order_id>/status/", AdminOrderStatusUpdateAPIView.as_view(), name="admin-order-status"),
    path("admin/orders/overview/", AdminOrderOverviewAPIView.as_view()),
    path("send-notification/", AdminSendNotificationAPIView.as_view()),

]
