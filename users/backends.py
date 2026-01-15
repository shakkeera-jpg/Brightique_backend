# # backends.py
# from django.contrib.auth.backends import ModelBackend
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class EmailBackend(ModelBackend):
#     def authenticate(self, request, email=None, password=None, **kwargs):
#         # print("EmailBackend called:", email, password)
#         if email is None or password is None:
#             return None
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             # print("User not found")
#             return None
#         if user.check_password(password):
#             # print("Password correct")
#             return user
#         print("Password incorrect")
#         return None
