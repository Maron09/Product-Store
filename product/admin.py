from django.contrib import admin
from .models import Category, Product, ProductImage



class ProductImageInline(admin.StackedInline):
    model = ProductImage
    extra = 5

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ('title',)}
    list_display = ('title', 'modified_at')
    search_fields = ('title',)


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ('name',)}
    list_display = ('name', 'category', 'get_vendor_business_name', 'price', 'slug', 'modified_at')
    search_fields = ('name', 'category__title', 'vendor__business_name', 'price')
    inlines = [ProductImageInline]
    
    def get_vendor_business_name(self, obj):
        return obj.vendor.business_name  
    
    get_vendor_business_name.short_description = 'Business Name'



admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)