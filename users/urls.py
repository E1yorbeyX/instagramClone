from django.urls import path
from .views import SingUpCreateAPIView, VerifyAPIView, GetCodeAPIView, ChangeUserInfo, ChangeUserPhotoAPIView, LoginSerializersView, TokenRefreshView, LogoutView, ForgotPasswordView, ResetPasswordView
urlpatterns = [
    path('login/', LoginSerializersView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/refresh/', TokenRefreshView.as_view(), name='refreshToken' ),
    path('signup/', SingUpCreateAPIView.as_view(), name="signup"),
    path('verify/', VerifyAPIView.as_view(), name="verify"),
    path('new-verify/', GetCodeAPIView.as_view(), name="new-verify"),
    path('update/', ChangeUserInfo.as_view(), name="update"),
    path('upload-image/', ChangeUserPhotoAPIView.as_view(), name="upload_image"),
    path('forgotpassword/', ForgotPasswordView.as_view(), name="forgot_password"),
    path('resetpassword/', ResetPasswordView.as_view(), name='reset_password')
]