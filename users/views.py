from django.shortcuts import render
from datetime import datetime
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.decorators import permission_classes
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView , TokenRefreshView
from shared.utiliy import check_email_or_phone
from .models import User, NEW, VERIFICATION, VIA_EMAIL, VIA_NUMBER
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from shared.utiliy import send_mail, send_number
from .serializers import SignUpSerializers, ChangeUserSerializers, ChangeUserPhotoSerializer, LoginSerializers, TokenRefreshSerializer, LogoutSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
class SingUpCreateAPIView(CreateAPIView):
    models = User
    permission_classes = (permissions.AllowAny, )
    serializer_class = SignUpSerializers

class VerifyAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        user = self.request.user
        code = self.request.data.get('code')

        self.check_verify(user, code)
        return Response(
            data= {
               "success": True,
               "access_token":user.token()['access'],
               "reflesh_token":user.token()['refresh_token'],
               "auth_status": user.auth_status
        }
    )

    @staticmethod
    def check_verify(user, code):
        verifeis = user.verfiy_conform.filter(exparition_time__gte=datetime.now(), code=code, is_conformed=False)
        if not verifeis.exists():
            data = {
                "message":["Bu kod invalid"]
            }
            raise ValidationError(data)
        else:
            verifeis.update(is_conformed=True)
        if user.auth_status == NEW:
            user.auth_status = VERIFICATION
            user.save()
        return True

class GetCodeAPIView(APIView):

    def get(self, request, *args, **kwargs):     
        user = self.request.user
        self.check_verify_code(user)
        if user.auth_type == VIA_EMAIL:
            code = user.create_code(VIA_EMAIL)
            send_mail(user, code)
        elif user.auth_type == VIA_NUMBER:
            code = user.create_code(VIA_NUMBER)
            send_mail(user, code)
        else:
            data = {
                "message":"Invalid email or phone number"
            }
        return Response(
            data = {
                "success":True,
                "message":"Code was will be send to you"
            }
        )

    
    def check_verify_code(self, user):
        verifeis = user.verfiy_conform.filter(exparition_time__gte=datetime.now(),  is_conformed=False)
        if verifeis.exists():
           data = {
             "message":"You have valid code. You must use this code!"
           }
           return ValidationError(data)

class ChangeUserInfo(UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ChangeUserSerializers
    http_method_names = ['patch', 'put']

    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        super(ChangeUserInfo, self).update(request, *args, **kwargs)
        data = {
            "success":True,
            "message":"Successfully update data",
            "auth_status":self.request.user.auth_status
        }
        return Response(data)
    
    def partial_update(self, request, *args, **kwargs):
        super(ChangeUserInfo, self).partial_update(request, *args, **kwargs)
        data = {
            "success":True,
            "message":"Successfully update data",
            "auth_status":self.request.user.auth_status
        }
        return Response(data)

class ChangeUserPhotoAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def put(self, request, *args, **kwargs):
        serializer = ChangeUserPhotoSerializer(data=request.data)
        if serializer.is_valid():
          user = request.user
          serializer.update(user, serializer.validated_data)
          return Response( {"message":"Rasm yuklandi"}, status=200)
        return Response( 
            serializer.errors, status=400
        )

class LoginSerializersView(TokenObtainPairView):
    serializer_class = LoginSerializers
    
class TokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

class LogoutView(APIView):
    serializer_class  = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        try:
            reflesh_token = self.request.data['refresh']
            token = RefreshToken(reflesh_token)
            token.blacklist()
            data = {
                "success":True,
                "message":"Muvoffaqiyatli logout qildiningiz"
            }
            return Response(data, status=205)
        except TokenError:
            return Response(status=400)

class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny,]
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        email_or_phone=serializer.validated_data.get('email_or_phone')
        user = serializer.validated_data.get('user')

        if check_email_or_phone(email_or_phone)== "email":
            code = user.create_code(VIA_EMAIL)
            send_mail(email_or_phone, code)

        elif check_email_or_phone(email_or_phone)== "phone":
            code = user.create_code(VIA_NUMBER)
            send_mail(email_or_phone)
        
        return Response(
            {
                "success":True,
                "message":"Tasdiqlash kodi yuborildi",
                "access":user.token()['access'],
                "refresh":user.token()['refresh_token'],
                "user_status":user.auth_status,         
            }, status=200
        )

class ResetPasswordView(UpdateAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    http_method_names = ['patch', 'put']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)  # o'zgartirish shu yerda

        try:
            user = User.objects.get(id=response.data.get('id'))
        except ObjectDoesNotExist as e:
            raise NotFound(detail="User not found")

        return Response({
            "success": True,
            "message": "Successfully reset your password",
            "access": user.token()['access'],
            "refresh": user.token()['refresh_token']
        })