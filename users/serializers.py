from typing import Any, Dict
from shared import utiliy
from shared.utiliy import check_user_input
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework import exceptions
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from django.db.models import Q 
from django.core.validators import FileExtensionValidator
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from .models import User, UserConfirmation, VIA_EMAIL, VIA_NUMBER, NEW, VERIFICATION, DONE, UPLOAD_IMAGE



class SignUpSerializers(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    
    def __init__(self, *args, **kwargs):
        super(SignUpSerializers, self).__init__(*args, **kwargs)
        self.fields['email_or_phone'] = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'auth_type',
            'auth_status',
        )
        extra_kwargs = {
            'auth_type':{'read_only':True, 'required':False},
            'auth_status':{'read_only':True, 'required':False}
        }
    def create(self, validated_data):
        user = super(SignUpSerializers, self).create(validated_data)
        print(user)
        if user.auth_type == VIA_EMAIL:
           code = user.create_code(VIA_EMAIL)
           utiliy.send_mail(user.email, code)
           user.save()
           return user
        elif user.auth_type == VIA_NUMBER:
            code = user.create_code(VIA_NUMBER)
            print(code)
            utiliy.send_mail(user.phone_number, code)
            # utiliy.send_number(user.phone_numbe, code)
            return user
             

    def validate(self, data):
        super(SignUpSerializers, self).validate(data)
        data = self.auth_validate(data)
        return data
    
    def auth_validate(self, data):
        print(data)
        user_data = str(data.get('email_or_phone')).lower()
        input_type = utiliy.check_email_or_phone(user_data)
        # print("user_input:", user_data, "\n", "input_type:", input_type)
        if  input_type == "email":
            data = {
                "email": user_data,
                "auth_type": VIA_EMAIL
            }
        elif input_type == "phone":
            data = {
                "email":user_data,
                "auth_type":VIA_NUMBER
            }
        else:
            data = {
                "email":False,
                "message":"You must input email or phone"
            }

        return data
    def validate_email_or_phone(self, value):
        value = value.lower()
        if value and User.objects.filter(email=value):
            data = {
               "success":False,
               "message":"Bu email allaqachon ruyxatdan o'tgan"
            }
            raise ValidationError(data)
        elif value and User.objects.filter(phone_number=value):
            data = {
               "success":False,
               "message":"Bu raqam allaqachon ruyxatdan o'tgan"
            }
            raise ValidationError(data)
        return value
   
    def to_representation(self, instance):
        data =  super(SignUpSerializers, self).to_representation(instance)
        data.update(instance.token())
        return data

class ChangeUserSerializers(serializers.Serializer):
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        password = data.get('password', None)
        confirm_password = data.get('confirm_password', None)

        if password != confirm_password:
            raise ValidationError ({
                "message":"Password va Confirm password bir xil emas !"
            })

        if password:
            validate_password(password)
            validate_password(confirm_password)
      
        return data
    
    def validate_username(self, username):
        if len(username)<5 or len(username)>35:
            raise ValidationError ({
                "message":"Username uzunligi max-35 min-5 bulishi kerak"
            })
        if username.isdigit():
            raise ValidationError ({
                "message":"Username faqat sonlardan iborat bo'lish mantiqsiz"
            })
        
        return username

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.username = validated_data.get('username', instance.username)
        instance.password = validated_data.get('password', instance.password)
        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))  
        if instance.auth_status == VERIFICATION:
            instance.auth_status = DONE
        instance.save()
        return instance

class ChangeUserPhotoSerializer(serializers.Serializer):
    photo = serializers.ImageField(validators=[FileExtensionValidator(allowed_extensions=['jpg','png'])])
    
    def update(self, instance, validated_data):
        photo = validated_data.get('photo')
        if photo:
            instance.photo = photo
            instance.auth_status= UPLOAD_IMAGE
            instance.save()
        return instance

class LoginSerializers(TokenObtainPairSerializer):

    def __init__(self, *args, **kwargs):
        super(LoginSerializers, self).__init__(*args, **kwargs)
        self.fields['userinput']=serializers.CharField(required=True)
        self.fields['username']=serializers.CharField(required=False, read_only=True)

    def auth_validate(self, data):
        user_input = data.get('userinput')
        if check_user_input(user_input) == "username":
            username = user_input
        elif check_user_input(user_input) == "email":
            user = self.get_user(email__iexact=user_input)
            username = user.username
        elif check_user_input(user_input) == "phone":
            user = self.get_user(phone_number=user_input)
            username = user.username
        else:
            data = {
                "success":False,
                "message":"Yaroqli qiymat kiritilmagan"
            }
            raise ValidationError(data)

        authentication_data = {
            self.username_field:username,
            "password":data['password']
        }
        current_user = User.objects.filter(username__iexact=username).first()
        if current_user.auth_status in [NEW, VERIFICATION]:
            data = {
                "success":False,
                "message":"Siz to'liq ruyxatdan o'tmagansiz"
            }

        user = authenticate(**authentication_data)
        if user is not None:
            self.user = user
        else:
            data = {
                "Success":False,
                "message":"Foydanuvchi topilmadi. Login yoki parol xato bulishi mumkin."
            }
            raise ValidationError(data)
    def validate(self, data):
        self.auth_validate(data)
        if self.user.auth_status not in [DONE, UPLOAD_IMAGE]:
            raise PermissionDenied("Sizga ruxsat yuq. To'liq registratsiya qilmagansiz")
        data = self.user.token()
        data['auth_status']=self.user.auth_status
        # data['access_token']=self.user.token()
        data['username']=self.user.username

        return data

    def get_user(self, **kwargs):
        user = User.objects.filter(**kwargs)
        if not user.exists():
            data = {
                "message":"User topilmayapti"
            } 
            raise ValidationError(data)
        return user.first()

class LoginRefreshSerializer(TokenRefreshSerializer):
    
    def validate(self, attrs):
       data = super().validate(attrs)
       access_token_instance = AccessToken(data['access'])
       user_id = access_token_instance('user_id')
       user = get_object_or_404(User, id=user_id)
       update_last_login(user)
       
       return data

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    
class ForgotPasswordSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(write_only=True, required=True)
    def validate(self, attrs):
        email_or_phone = attrs.get('email_or_phone', None)
        if email_or_phone is None:
            raise ValidationError(
                {
                    "success":False,
                    "message":"Please input your email or phone number"
                }
            )
        user = User.objects.filter(Q(email=email_or_phone) | Q(phone_number=email_or_phone))
        if not user.exists():
            raise ValidationError(
                {
                    "success":False,
                    "message":"User not found"
                }
            )
        attrs['user'] = user.first()
        return attrs

class ResetPasswordSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model=User
        fields = (
            'id',
            'password',
            'confirm_password'
        )

        def validate(self, data):
            password= data.get('password', None)
            confirm= data.get('confirm_password', None)
            if password != confirm_password:
                raise ValidationError(
                    {
                        "success":False,
                        "message":"Sizning password va cofirm password maydonlaringiz bir biridan farq qilyapti"
                    }
                )
            if password:
                validate_password(password)
            return data

        def update(self, instance, validated_data):
            password = validated_data.pop('password')
            instance.set_password(password)

            return super(ResetPasswordSerializer, self).update(instance, validated_data)