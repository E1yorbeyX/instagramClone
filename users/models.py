from typing import Iterable
from django.db import models
import uuid
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AbstractUser
from shared.models import Base
import random
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta

ORDIRAY_USER, MANAGER, ADMIN = ('ordiray_user', 'manager', 'admin')
VIA_EMAIL, VIA_NUMBER = ('via_email', 'via_number')
NEW, VERIFICATION, DONE, UPLOAD_IMAGE = ('new', 'verification', 'done', 'upload_image')

# Create your models here.
class User(AbstractUser, Base):
    # add additional fields in here
    USER_ROLES = (
        (ORDIRAY_USER, ORDIRAY_USER),
        (MANAGER, MANAGER),
        (ADMIN, ADMIN)
    )
    AUTH_TYPE_CHOICES = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_NUMBER, VIA_NUMBER)
    )
    AUTH_STATUS_CHOICES = (
        (NEW, NEW),
        (VERIFICATION, VERIFICATION),
        (DONE, DONE),
        (UPLOAD_IMAGE, UPLOAD_IMAGE)
    )

    user_roles = models.CharField(max_length=31, choices=USER_ROLES, default=ORDIRAY_USER)
    auth_type = models.CharField(max_length=31, choices=AUTH_TYPE_CHOICES)
    auth_status = models.CharField(max_length=31, choices=AUTH_STATUS_CHOICES, default=NEW)
    email = models.EmailField(null=True, blank=True, unique=True)
    phone_number = models.CharField(max_length=31, null=True, blank=True)
    image = models.ImageField(upload_to='user_photos/', null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=['jpg','png'])])
    def __str__(self):
        return self.username
    
    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def create_code(self, verfiy_type):
       code = random.randint(1000, 10000)

       UserConfirmation.objects.create(
           user_id=self.id,
           verfiy_type=verfiy_type,
           code = code
       )
       return code
    
    def check_username(self):
        if not self.username:
            temp_username = str(uuid.uuid4()).split('-')[-1]
            while User.objects.filter(username=temp_username):
                temp_username = f'{temp_username}{random.randint(0,9)}'
            self.username = temp_username

    def check_email(self):
        if self.email:
            self.email = self.email.lower()

    def check_pass(self):
        if not self.password:
           self.password = str(uuid.uuid4()).split('-')[-1]
    def hashing_password(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)
     
    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            'access':str(refresh.access_token),
            'refresh_token':str(refresh)
        }
        
    def save(self, *args, **kwargs):
        self.clean()
        super(User, self).save(*args, **kwargs)

    def clean(self) -> None:
        self.check_email()
        self.check_username()
        self.check_pass()
        self.hashing_password()


EMAIL_EXPIRE = 3
PHONE_EXPIRE = 2
class UserConfirmation(Base):
    VERFIY_TYPE = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_NUMBER, VIA_NUMBER)
    )
    verfiy_type = models.CharField(max_length=31, choices=VERFIY_TYPE)
    user = models.ForeignKey("users.User", related_name="verfiy_conform", on_delete=models.CASCADE)
    code = models.CharField(max_length=4)
    exparition_time = models.DateTimeField(null=True)
    is_conformed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.__str__())
    
    def save(self, *args, **kwargs):
        if self.verfiy_type == VIA_EMAIL:
            self.exparition_time = datetime.now() + timedelta(minutes=EMAIL_EXPIRE)
        elif self.verfiy_type == VIA_NUMBER:
            self.exparition_time == datetime.now()  + timedelta(minutes=PHONE_EXPIRE)
        super(UserConfirmation, self).save(*args, **kwargs)