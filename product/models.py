from django.db import models
from cloudinary.models import CloudinaryField
from authentication.models import User





class Category(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, default=None, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
    
    
    def clean(self):
        self.title = self.title.capitalize()
    
    
    def __str__(self):
        return self.title



class Product(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name='products')
    slug = models.SlugField(max_length=300, unique=True)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    stock = models.IntegerField()
    in_stock = models.BooleanField(default=False)
    discount = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return self.name.capitalize()



class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('product_images')
    
    def __str__(self):
        return f"Image for {self.product.name}"