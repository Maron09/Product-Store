from rest_framework import serializers
from authentication.models import Userprofile, User



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