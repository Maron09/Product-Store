from django.db import models
from cloudinary.models import CloudinaryField
from authentication.models import User
from django.utils.text import slugify


class Category(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
    
    def save(self, *args, **kwargs):
        if not self.slug or self.title != Category.objects.get(pk=self.pk).title:
            self.slug = f"{slugify(self.title)}-{self.id}"  
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Product(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name='products')
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    stock = models.IntegerField()
    discount = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    @property
    def in_stock(self):
        return self.stock > 0  

    def save(self, *args, **kwargs):
        self.name = self.name.capitalize()
        if not self.slug:
            self.slug = slugify(self.name)
        if self.price < 0:
            raise ValueError("Price cannot be negative")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('product_images')

    def __str__(self):
        return f"Image for {self.product.name}"
