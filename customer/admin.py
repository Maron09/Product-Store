from django.contrib import admin
from .models import WishList

class WishListAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'product')

    def full_name(self, obj):
        return f"{obj.customer.first_name} {obj.customer.last_name}"
    full_name.admin_order_field = "customer__first_name" 
    full_name.short_description = "Full Name"
    



admin.site.register(WishList, WishListAdmin)
