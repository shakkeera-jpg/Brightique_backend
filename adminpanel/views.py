from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models
from products.models import Product
from order.models import Order, OrderItem
from users.models import User
from .permissions import IsAdminUserCustom
from rest_framework import status
from .serializers import AdminUserSerializer,AdminProductSerializer
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum, F, FloatField, Q
from order.serializers import OrderSerializer
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncDate
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.permissions import IsAdminUser
from notifications.models import Notification



class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def get(self, request):
        
        total_products = Product.objects.count()
        total_orders = Order.objects.count()
        total_users = User.objects.count()

       
        in_stock = Product.objects.filter(stock__gt=0).count()
        out_of_stock = Product.objects.filter(stock=0).count()

        
        stock_per_category = []
        for key, label in Product.CATEGORY_CHOICES:
            total_stock = Product.objects.filter(category=key).aggregate(
                total=models.Sum("stock")
            )["total"] or 0

            stock_per_category.append({
                "category": label,
                "stock": total_stock
            })

        
        orders_per_category = []
        for key, label in Product.CATEGORY_CHOICES:
            total_orders_category = OrderItem.objects.filter(
                product__category=key,
                order__status__in=["pending", "confirmed"]
            ).aggregate(
                total=models.Sum("quantity")
            )["total"] or 0

            orders_per_category.append({
                "category": label,
                "orders": total_orders_category
            })

        total_revenue = OrderItem.objects.filter(
            order__status__in=["pending", "confirmed", "delivered"]
        ).aggregate(
            revenue=Sum(F("quantity") * F("price"), output_field=FloatField())
        )["revenue"] or 0

        
        revenue_per_category = []
        for key, label in Product.CATEGORY_CHOICES:
            revenue = OrderItem.objects.filter(
                product__category=key,
                order__status__in=["pending", "confirmed", "delivered"]
            ).aggregate(
                total=Sum(F("quantity") * F("price"), output_field=FloatField())
            )["total"] or 0

            revenue_per_category.append({
                "category": label,
                "revenue": revenue
            })

        
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)

        revenue_qs = OrderItem.objects.filter(
            order__status__in=["pending", "confirmed", "delivered"],
            order__created_at__date__gte=thirty_days_ago
        ).annotate(date=TruncDate("order__created_at")).values("date").annotate(
            daily_revenue=Sum(F("quantity") * F("price"), output_field=FloatField())
        ).order_by("date")

        revenue_over_time = [
            {"date": r["date"].strftime("%Y-%m-%d"), "revenue": r["daily_revenue"]} for r in revenue_qs
        ]    

        return Response({
            "total_products": total_products,
            "total_orders": total_orders,
            "total_users": total_users,

            "in_stock": in_stock,
            "out_of_stock": out_of_stock,

            "stock_per_category": stock_per_category,
            "orders_per_category": orders_per_category,

            "total_revenue": total_revenue,
            "revenue_per_category": revenue_per_category,
            "revenue_over_time": revenue_over_time,
        })    


class AdminUserListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def get(self, request):
        users = User.objects.all().order_by("-created_at")
        page = request.GET.get("page", 1)

        page_size = 5

        base_queryset = User.objects.all()

        overview = {
            "total": base_queryset.count(),
            "admins": base_queryset.filter(role="admin").count(),
            "users": base_queryset.filter(role="user").count(),
            "blocked": base_queryset.filter(is_blocked=True).count(),
        }

        search = request.GET.get("search")
        if search:
            users = users.filter(name__icontains=search)

        role = request.GET.get("role")
        if role and role != "all":
            users = users.filter(role=role)
        paginator = Paginator(users, page_size)

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        serializer = AdminUserSerializer(page_obj.object_list, many=True)

        return Response({
            "results": serializer.data,
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number,
            "next": page_obj.number + 1 if page_obj.has_next() else None,
            "previous": page_obj.number - 1 if page_obj.has_previous() else None,
            "overview": overview,
        })    

        


class AdminUserDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    def get(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminUserSerializer(user)
        return Response(serializer.data)

    def patch(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

       
        if "is_blocked" not in request.data:
            return Response(
                {"detail": "Only 'is_blocked' can be updated"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_blocked = request.data.get("is_blocked")
        user.save()

        serializer = AdminUserSerializer(user)
        return Response(serializer.data)
    

class AdminProductListCreateView(APIView):
    permission_classes = [IsAdminUserCustom]

    def get(self, request):
        search = request.GET.get("search", "")
        category = request.GET.get("category", "")
        try:
            page_number = int(request.GET.get("page", 1))
        except ValueError:
            page_number = 1

        page_size = 5

        products = Product.objects.all().order_by("-id")

        
        if search:
            products = products.filter(name__icontains=search)

        
        if category:
            products = products.filter(category=category)


        paginator = Paginator(products, page_size)
        page = paginator.get_page(page_number)

        serializer = AdminProductSerializer(page, many=True)

        return Response({
            "results": serializer.data,
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page.number,
            "next": page.number + 1 if page.has_next() else None,
            "previous": page.number - 1 if page.has_previous() else None,
        })

class AdminCategoryListView(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        categories = [
            {"value": key, "label": label} for key, label in Product.CATEGORY_CHOICES
        ]
        return Response(categories)        
    
    def post(self, request):
        serializer = AdminProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class AdminProductDetailView(APIView):
    permission_classes = [IsAdminUserCustom]

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = AdminProductSerializer(product)
        return Response(serializer.data)

    def patch(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = AdminProductSerializer(
            product,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return Response(
            {"message": "Product deleted successfully"},
            status=204
        )


class AdminOrderListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def get(self, request):
        """
        GET /admin/orders/?status=pending&search=john&page=1
        """
        orders = Order.objects.prefetch_related("items").select_related("user").order_by("-created_at")

        
        search = request.GET.get("search")
        if search:
            orders = orders.filter(
                Q(user__name__icontains=search) | Q(user__email__icontains=search)
            )

        
        status_filter = request.GET.get("status")
        if status_filter:
            orders = orders.filter(status__iexact=status_filter)

        
        try:
            page_number = int(request.GET.get("page", 1))
        except ValueError:
            page_number = 1
        page_size = 2  

        paginator = Paginator(orders, page_size)
        page = paginator.get_page(page_number)

        serializer = OrderSerializer(page, many=True)

        return Response({
            "results": serializer.data,
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page.number,
            "next": page.number + 1 if page.has_next() else None,
            "previous": page.number - 1 if page.has_previous() else None,
        }, status=200)

class AdminOrderStatusUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def patch(self, request, order_id):
        """
        PATCH /admin/orders/<order_id>/status/
        Body: { "status": "delivered" }
        """
        order = get_object_or_404(Order, id=order_id)
        new_status = request.data.get("status")

        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({"detail": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status

        if new_status == "delivered":
            order.is_paid = True
        order.save(update_fields=["status","is_paid"])

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminOrderOverviewAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def get(self, request):
        qs = Order.objects.all()

        processing_count = qs.filter(
            status__in=["pending", "confirmed"]
        ).count()

        return Response({
            "total": qs.count(),
            "processing": processing_count,   
            "delivered": qs.filter(status="delivered").count(),
            "cancelled": qs.filter(status="cancelled").count(),
        })
    

class AdminSendNotificationAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        print("🔥 ADMIN SEND NOTIFICATION HIT")
        user_id = request.data.get("user_id")
        title = request.data.get("title")
        message = request.data.get("message")

        if not title or not message:
            return Response({"error": "Title and message required"}, status=400)

        users = User.objects.filter(id=user_id) if user_id else User.objects.all()

        channel_layer = get_channel_layer()

        for user in users:
            notification = Notification.objects.create(
                user=user,
                title=title,
                message=message
            )

            async_to_sync(channel_layer.group_send)(
                f"user_{user.id}",
                {
                    "type": "send_notification",
                    "data": {
                        "id": notification.id,
                        "title": notification.title,
                        "message": notification.message,
                        "is_read": notification.is_read,
                        "created_at": str(notification.created_at),
                    }
                }
            )

        return Response({"success": True})

