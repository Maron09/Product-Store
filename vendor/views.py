from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from authentication.models import Userprofile, User
from .serializers import VendorProfileSerializer
from authentication.permissions import IsVendor



class VendorProfileView(GenericAPIView):
    serializer_class = VendorProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsVendor]
    
    
    def get_object(self):
        user = self.request.user
        profile, _ = Userprofile.objects.get_or_create(user=user)
        return profile
    
    @swagger_auto_schema(
        operation_description="Retrieve vendor profile",
        responses={200: VendorProfileSerializer()}
    )
    def get(self, request):
        
        profile = self.get_object()
        if profile is None:
            return Response (
                {
                    "success": False,
                    "message": "You are not authorized to access this."
                },
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = self.serializer_class(profile)
        return Response(
            {
                "success": True,
                "message": serializer.data
            },
            status=status.HTTP_200_OK
        )
        
    @swagger_auto_schema(
        operation_description="Update vendor profile and user details",
        request_body=VendorProfileSerializer,
        responses={200: "Vendor profile updated successfully", 400: "Invalid data"}
    )
    def put(self, request):
        
        
        profile = self.get_object()
        if profile is None:
            return Response (
                {
                    "success": False,
                    "message": "You are not authorized to access this."
                },
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = self.serializer_class(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Vendor profile updated successfully",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                "success": False,
                "message": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

