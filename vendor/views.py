from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from authentication.models import Userprofile
from .serializers import VendorProfileSerializer, CategorySerializer, ProductSerializer, ProductImageSerializer
from authentication.permissions import IsVendor
from product.models import Category, Product, ProductImage
from django.http import Http404
from .pagination import CombinedPagination
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404









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
    def patch(self, request):
        
        
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


class CategoryView(GenericAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    
    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return  [permissions.IsAuthenticated(), permissions.IsAdminUser()]
    
    
    def get(self, request):
        
        categories = self.get_queryset()
        serializer = self.serializer_class(categories, many=True)
        return Response(
            {
                "success": True,
                "message": "Categories retrieved successfully",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @transaction.atomic
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            title = serializer.validated_data.get("title")
            if Category.objects.filter(title__iexact=title).exists():
                return Response(
                    {
                        "success": False,
                        "message": "Category Already Exists"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Category created successfully",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                "success": False,
                "message": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )



class CategoryDetailView(GenericAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            raise Http404
    
    def get(self, request, pk):
        category = self.get_object(pk=pk)
        serializer = CategorySerializer(category)
        return Response(
            {
                "success": True,
                "message": serializer.data
            }
        )
    
    @transaction.atomic
    def patch(self, request, pk):
        category = self.get_object(pk=pk)
        serializer = self.serializer_class(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Category Updated Successfully",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                "success": False,
                "message": serializer.errors
            }
        )
    
    
    @transaction.atomic
    def delete(self, request, pk):
        category = self.get_object(pk=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductView(GenericAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    pagination_class = CombinedPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    
    
    
    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return  [IsVendor()]
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("name", openapi.IN_QUERY, description="Filter by name", type=openapi.TYPE_STRING),
            openapi.Parameter("category", openapi.IN_QUERY, description="Filter by category", type=openapi.TYPE_STRING),
            openapi.Parameter("min_price", openapi.IN_QUERY, description="Minimum price", type=openapi.TYPE_NUMBER),
            openapi.Parameter("max_price", openapi.IN_QUERY, description="Maximum price", type=openapi.TYPE_NUMBER),
        ]
    )
    
    
    def get(self, request):
        products = self.filter_queryset(self.get_queryset())
        paginated_products = self.paginate_queryset(products)
        if paginated_products is not None:
            serializer = self.serializer_class(paginated_products, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.serializer_class(products, many=True)
        return Response(
            {
                "success": True,
                "message": "Products Retrieved Successflly",
                "data": serializer.data
            }
        )
    
    @transaction.atomic
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Category created successfully",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                "success": False,
                "message": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )



class ProductDetailView(GenericAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    
    
    def get_permissions(self):
        """Allow anyone to view, but only vendors to modify"""
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [IsVendor()]
    
    def get_object(self, pk, check_owner=False):
        """Retrieve product, and optionally enforce ownership check"""
        try:
            product = Product.objects.get(pk=pk)
            if check_owner and product.vendor != self.request.user:
                raise PermissionDenied("You do not have permission to modify this product.")
            return product
        except Product.DoesNotExist:
            raise Http404
    
    def get(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(
            {
                "success": True,
                "message": serializer.data
            }
        )
    
    @transaction.atomic
    def patch(self, request, pk):
        product = self.get_object(pk, check_owner=True)
        serializer = self.serializer_class(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Product Updated Successfully",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                "success": False,
                "message": serializer.errors
            }
        )
    
    @transaction.atomic
    def delete(self, request, pk):
        product = self.get_object(pk, check_owner=True)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class ProductImageUploadView(GenericAPIView):
    serializer_class = ProductImageSerializer
    permission_classes = [IsVendor]
    parser_classes = [MultiPartParser, FormParser]  

    def put(self, request, product_id):
        """
        Upload multiple images for a product (Max 5 images).
        """
        product = get_object_or_404(Product, id=product_id, vendor=request.user)

        
        if product.images.count() >= 5:
            return Response(
                {"success": False, "message": "You can only upload up to 5 images per product."},
                status=status.HTTP_400_BAD_REQUEST
            )

        
        images = request.FILES.getlist('image')  

        if not images:
            return Response({"success": False, "message": "No images provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the total count does not exceed 5
        if product.images.count() + len(images) > 5:
            return Response(
                {"success": False, "message": f"Only {5 - product.images.count()} more images can be uploaded."},
                status=status.HTTP_400_BAD_REQUEST
            )

        uploaded_images = []
        with transaction.atomic():
            for image in images:
                product_image = ProductImage.objects.create(product=product, image=image)
                uploaded_images.append(ProductImageSerializer(product_image).data)

        return Response(
            {
                "success": True,
                "message": "Images uploaded successfully.",
                "data": uploaded_images
            },
            status=status.HTTP_200_OK
        )