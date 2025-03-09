from django.contrib import admin
from .models import User, Userprofile, EmailOTP, PasswordResetToken
from django.contrib.auth.admin import UserAdmin



class CustomUserAdmin(UserAdmin):
    list_display = ('email','first_name', 'last_name', 'role', 'business_name', 'is_active')
    ordering = ('-date_joined',)
    filter_horizontal = ()
    list_filter = []
    fieldsets = ()


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["full_name", "profile_pic"]

    def full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    full_name.admin_order_field = "user__first_name" 
    full_name.short_description = "Full Name"
    
admin.site.register(User, CustomUserAdmin)
admin.site.register(Userprofile, UserProfileAdmin)
admin.site.register(EmailOTP)
admin.site.register(PasswordResetToken)