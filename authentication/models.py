from django.db import models
from .manager import UserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.timezone import now
import random
from datetime import timedelta
from cloudinary.models import CloudinaryField
import uuid


class User(AbstractBaseUser, PermissionsMixin):
    VENDOR = 1
    CUSTOMER = 2
    
    ROLE_CHOICE =  (
        (VENDOR, "Vendor"),
        (CUSTOMER, "Customer")
    )
    
    first_name = models.CharField(max_length=200, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=200, verbose_name=_("Last Name"))
    email = models.EmailField(unique=True, max_length=100, verbose_name=_("Email Address"))
    phone_number = models.CharField(max_length=14, blank=True, null=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICE, blank=True, null=True)
    business_name = models.CharField(max_length=255, blank=True, null=True)
    
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()
    
    def __str__(self):
        return self.email
    
    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True
    
    def is_vendor(self):
        return self.role == self.VENDOR
    
    def is_customer(self):
        return self.role == self.CUSTOMER
    
    def token(self):
        refresh = RefreshToken.for_user(self)
        refresh["role"] = self.role
        return {
            'refresh' : str(refresh),
            'access' : str(refresh.access_token)
        }
    
    def save(self, *args, **kwargs):
        self.first_name = self.first_name.title()
        self.last_name = self.last_name.title()
        super().save(*args, **kwargs)



class Userprofile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    profile_pic = CloudinaryField("profile_pic", null=True, blank=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class EmailOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="email_otp")
    code = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return f"{self.user.email} {self.code}"
    
    def generate_otp(self):
        """Generate a 6-digit OTP"""
        self.code = str(random.randint(100000, 999999))
        self.created_at = now()
        self.save()
    
    def is_valid(self):
        """Check if OTP is within the 5-minute window"""
        return now() < self.created_at + timedelta(minutes=5)



class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def is_expired(self):
        return (now() - self.created_at).total_seconds() > 1800