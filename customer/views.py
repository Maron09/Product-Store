from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from authentication.models import Userprofile
from .serializers import CustomerProfileSerializer
from authentication.permissions import IsCustomer
from django.utils.functional import cached_property
from .serializers import WishListSerializer
from .models import WishList
from product.models import Product
from django.shortcuts import get_object_or_404
from rest_framework.parsers import JSONParser




class CustomerProfileView(GenericAPIView):
    serializer_class = CustomerProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]
    
    
    @cached_property
    def profile(self):
        user = self.request.user
        profile, _ = Userprofile.objects.get_or_create(user=user)
        return profile

    @swagger_auto_schema(
        operation_description="Retrieve the authenticated customer's profile details.",
        responses={200: CustomerProfileSerializer()}
    )

    
    def get(self, request):
        serializer = self.serializer_class(self.profile)
        return Response(
            {"success": True, "message": serializer.data},
            status=status.HTTP_200_OK
        )
    
    
    @swagger_auto_schema(
        operation_description="Update the authenticated customer profile. Partial updates are allowed.",
        request_body=CustomerProfileSerializer(partial=True),
        responses={
            200: openapi.Response(
                description="Customer profile updated successfully",
                schema=CustomerProfileSerializer()
            ),
            400: openapi.Response(description="Validation errors"),
        }
    )
    
    @transaction.atomic
    def patch(self, request):
        """
        Update the authenticated customer's profile.
        """
        serializer = self.serializer_class(self.profile, data=request.data, partial=True)
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



class WishlistView(GenericAPIView):
    serializer_class = WishListSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]
    queryset = WishList.objects.all()
    parser_classes = [JSONParser]
    
    def get_parser_classes(self):
        if self.request.method == "DELETE":
            return [JSONParser()]
        return super().get_parser_classes()
    
    @swagger_auto_schema(
        operation_description="Retrieve the authenticated customer's wishlist.",
        responses={200: WishListSerializer(many=True)}
    )
    
    def get(self, request):
        """Fetch the wishlist of the authenticated customer."""
        wishlist = WishList.objects.filter(customer=request.user)
        serializer = self.serializer_class(wishlist, many=True)
        return Response(
            {
                "success": True,
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @swagger_auto_schema(
        operation_description="Add a product to the wishlist.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'product': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the product to add")
            },
            required=['product']
        ),
        responses={
            201: openapi.Response(
                description="Product added to wishlist",
                schema=WishListSerializer()
            ),
            400: openapi.Response(description="Product is already in wishlist or invalid data"),
        }
    )
    
    @transaction.atomic
    def post(self, request):
        product_id = request.data.get("product")
        product = get_object_or_404(Product, id=product_id)
        
        if WishList.objects.filter(customer=request.user, product=product).exists():
            return Response(
                {
                    "success": False,
                    "message": "Product is already in your wishlist."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        wishlist_item = WishList.objects.create(customer=request.user, product=product)
        serializer = self.serializer_class(wishlist_item)
        return Response(
            {
                "success": True,
                "message": "Product saved to wishlist",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    @swagger_auto_schema(
        operation_description="Remove a product from the wishlist.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'product': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the product to remove")
            },
            required=['product']
        ),
        responses={
            200: openapi.Response(description="Product removed from wishlist"),
            400: openapi.Response(description="Product ID is required or not found"),
        }
    )
    
    @transaction.atomic
    def delete(self, request):
        product_id = request.data.get("product")
        if not product_id:
            return Response(
                {"success": False, "message": "Product ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        wishlist_item = get_object_or_404(WishList, customer=request.user, product_id=product_id)
        wishlist_item.delete()
        return Response(
            {
                "success": True,
                "message": "Product removed from wishlist.",
            },
            status=status.HTTP_200_OK
        )