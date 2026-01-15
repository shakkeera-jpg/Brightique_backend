from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.encoding import force_bytes
from rest_framework import status
from .serializers import SignupSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import EmailTokenObtainPairSerializer
from .serializers import UserProfileSerializer
from rest_framework.permissions import IsAuthenticated
from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_str
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

User = get_user_model()

class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
    


class SignupAPIView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Signup successful"}, status=201)
        return Response(serializer.errors, status=400)
    

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)


class GoogleAuthView(APIView):
    def post(self, request):
        token = request.data.get("token")

        if not token:
            return Response(
                {"error": "Token missing"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
           
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )

            email = idinfo["email"]
            name = idinfo.get("name", "")

            
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "name": name,
                    "is_active": True,
                }
            )

            if user.is_blocked:
                raise AuthenticationFailed(
                "Your account has been blocked by the admin"
            )
            
            refresh = RefreshToken.for_user(user)

            return Response({
    "access": str(refresh.access_token),
    "refresh": str(refresh),
    "user": {  
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "is_admin": user.is_staff,
    }
}, status=status.HTTP_200_OK)

        except ValueError:
            return Response(
                {"error": "Invalid Google token"},
                status=status.HTTP_400_BAD_REQUEST
            )




class PasswordResetRequestAPIView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)

        
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk)) 
        
        reset_link = f"http://localhost:5173/reset-password/{uid}/{token}"

        
        send_mail(
            "Password Reset",
            f"Click the link to reset your password: {reset_link}",
            "no-reply@example.com",
            [email],
            fail_silently=False,
        )

        return Response({"message": "Password reset link sent to your email"}, status=status.HTTP_200_OK)


class PasswordResetConfirmAPIView(APIView):
    def post(self, request, uid, token):
        password = request.data.get("password")
        if not password:
            return Response({"error": "Password required"}, status=400)

        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({"error": "Invalid reset link"}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=400)


        user.set_password(password)
        user.save()

        return Response({"message": "Password reset successful"}, status=200)