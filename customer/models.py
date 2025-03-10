from django.db import models
from authentication.models import User
from product.models import Product



class WishList(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlists")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlists")
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    class Meta:
        unique_together = ('customer', 'product')
    
    def __str__(self):
        return f"{self.customer.email} - {self.product.name}"
