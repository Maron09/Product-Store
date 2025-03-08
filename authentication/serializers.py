from rest_framework import serializers
from .models import User, PasswordResetToken
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed






class CustomerSignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    password2 = serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')  
        validated_data['role'] = User.CUSTOMER 
        return User.objects.create_user(**validated_data)



class VendorSignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    password2 = serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'business_name', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Passwords do not match")

        if not attrs.get('business_name'):
            raise serializers.ValidationError("Business name is required for vendors.")
            
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2') 
        validated_data['role'] = User.VENDOR  
        return User.objects.create_user(**validated_data)


class RequestNewOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=6)
    password = serializers.CharField(write_only=True, max_length=68)
    full_name = serializers.CharField(max_length=255, read_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'full_name', 'access_token', 'refresh_token']
    
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        
        request = self.context.get("request")
        
        user = authenticate(request=request, email=email, password=password)
        
        if not user:
            raise AuthenticationFailed("Invalid Credentials")
        if not user.is_active:
            raise AuthenticationFailed("Account not active")
        
        user_token = user.token()
        return {
            "email": email,
            "id": user.id,
            "full_name": user.get_full_name,
            "access_token": str(user_token.get("access")),
            "refresh_token": str(user_token.get("refresh"))
        }



class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()



class PasswordRestRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate(self, data):
        email = data.get("email") 
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("User with this email does not exist")
        return data 
    
    def create(self, validated_data):
        user = User.objects.get(email=validated_data["email"])
        PasswordResetToken.objects.create(user=user)
        return validated_data



class PasswordResetSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)
    
    def validate(self, data):
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")
        try:
            reset_token = PasswordResetToken.objects.get(token=data["token"])
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Invalid Token")
        
        if reset_token.is_expired():
            raise serializers.ValidationError("Token Has Expired")
        
        if new_password != confirm_password:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        
        
        data["user"] = reset_token.user
        
        return data
    
    
    def save(self):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.save()
        
        PasswordResetToken.objects.filter(user=user).delete() 
    