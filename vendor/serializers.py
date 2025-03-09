from rest_framework import serializers
from authentication.models import Userprofile, User
from product.models import Category, Product, ProductImage
from django.utils.text import slugify


class VendorProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    phone_number = serializers.CharField(source="user.phone_number", required=False)
    business_name = serializers.CharField(source="user.business_name", required=False)
    email = serializers.EmailField(source="user.email", required=False)
    profile_pic = serializers.SerializerMethodField() 

    class Meta:
        model = Userprofile
        fields = ["profile_pic", "first_name", "last_name", "phone_number", "business_name", "address", "email"]
        
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



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "title", "slug", "created_at"]
        read_only_fields = ["id", "slug", "created_at", "modified_at"]


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.FileField()
    
    class Meta:
        model = ProductImage
        fields = ["id", "image"]
    
    def to_representation(self, instance):
        """Customize response to return image URL."""
        return {"id": instance.id, "image_url": instance.image.url}
    
    def validate_product_pic(self, value):
        valid_extensions = ["jpg", "jpeg", "png"]
        file_extension = value.name.split(".")[-1].lower()
        
        if file_extension not in valid_extensions:
            raise serializers.ValidationError("Invalid file type. Only JPG, JPEG, and PNG are allowed.")
        return value

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )
    images = ProductImageSerializer(many=True, read_only=True)
    business_name = serializers.CharField(source="vendor.business_name", read_only=True)
    
    
    class Meta:
        model = Product
        fields = ["id", "vendor", "business_name", "name", "description", "category", "category_id", "slug", "price", "stock", "discount", "created_at", "modified_at", "images"]
        read_only_fields = ["id", "vendor", "slug", "category", "created_at", "modified_at"]
    
    def create(self, validated_data):
        request = self.context.get("request")  # Get request context
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError({"vendor": "User must be authenticated."})

        name = validated_data.get("name")
        vendor = request.user
        product = Product.objects.create(vendor=vendor, **validated_data)
        product.slug = f"{slugify(name)}-{product.id}"  
        product.save()
        return product