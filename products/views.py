from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Product
from .serializers import ProductSerializer
from rest_framework.response import Response
from math import ceil
from rest_framework.generics import RetrieveAPIView


class ProductPagination(PageNumberPagination):
    page_size = 8                     
    page_size_query_param = "page_size"
    max_page_size = 50

    def get_paginated_response(self, data):
        total_count = self.page.paginator.count
        page_size = self.get_page_size(self.request)
        total_pages = ceil(total_count / page_size) if page_size else 1
        current_page = self.page.number

        return Response({
            "products": data,
            "pagination": {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "page_size": self.page_size,
                "current_page": current_page,
                "total_pages": total_pages
            }
        })

class ProductListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductPagination

    filter_backends = [SearchFilter, OrderingFilter]   
    search_fields = ["name"]                           
    ordering_fields = ["price"]                       
    ordering = ["id"]                                  

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get("category")

        if category:
            queryset = queryset.filter(category__iexact=category)

        return queryset


class ProductDetailView(RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer