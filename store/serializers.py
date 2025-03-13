from rest_framework import serializers
from . models import Cart
from product.models import Product
from vendor.serializers import ProductSerializer


class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = Cart
        fields = ['id', 'product', 'quantity', 'total_price']
        read_only_fields = ['total_price']
    
    
    def validate(self, data):
        if data.get('quantity', 1) < 1:
            raise serializers.ValidationError({"quantity": "Quantity must be at least 1."})
        return data
    
    
    def create(self, validated_data):
        request = self.context["request"]
        product_id = request.data.get("product")  
        
        if not product_id:
            raise serializers.ValidationError({"product": "This field is required."})
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({"product": "Invalid product ID."})

        customer = request.user
        quantity = validated_data["quantity"]

        cart_item, created = Cart.objects.get_or_create(
            customer=customer,
            product=product,
            defaults={"quantity": quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return cart_item
