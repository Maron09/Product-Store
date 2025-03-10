from rest_framework import serializers
from authentication.models import Userprofile
from .models import WishList






class CustomerProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    phone_number = serializers.CharField(source="user.phone_number", required=False)
    email = serializers.EmailField(source="user.email", required=False)
    profile_pic = serializers.SerializerMethodField() 

    class Meta:
        model = Userprofile
        fields = ["profile_pic", "first_name", "last_name", "phone_number", "address", "email"]
        
    def get_profile_pic(self, obj):
        
        if obj.profile_pic:
            return obj.profile_pic.url
        return None
    
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()
    
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance



class WishListSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_price = serializers.ReadOnlyField(source='product.price')
    
    
    class Meta:
        model = WishList
        fields = ["id", "product", "product_name", "product_price", "created_at"]