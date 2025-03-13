from django.db import models
from authentication.models import User
from product.models import Product




class Cart(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    class Meta:
        unique_together = ('customer', 'product')
    
    def __str__(self):
        return f"{self.customer.get_full_name} - {self.product.name} (X{self.quantity})"
    
    
    @property
    def total_price(self):
        return self.product.price * self.quantity