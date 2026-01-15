from django.urls import path
from .views import UserNotificationsAPIView,MarkAllReadAPIView

urlpatterns = [
    path("my/", UserNotificationsAPIView.as_view()),
    path("mark-read/", MarkAllReadAPIView.as_view()),
]
