from django.urls import path
from .views import SignupAPIView,EmailTokenObtainPairView,UserProfileView,GoogleAuthView,PasswordResetRequestAPIView,PasswordResetConfirmAPIView
from rest_framework_simplejwt.views import(
    TokenRefreshView,
)

urlpatterns = [
    path('login/',EmailTokenObtainPairView.as_view()),
    path('token/refresh/',TokenRefreshView.as_view()),
    path('register/',SignupAPIView.as_view()),
    path("profile/", UserProfileView.as_view()),
    path("auth/google/", GoogleAuthView.as_view()),

    path("password-reset/", PasswordResetRequestAPIView.as_view(), name="password_reset_request"),
    path("password-reset-confirm/<str:uid>/<str:token>/", PasswordResetConfirmAPIView.as_view(), name="password_reset_confirm"),
]
