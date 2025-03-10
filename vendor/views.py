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
from django.utils.functional import cached_property









class VendorProfileView(GenericAPIView):
    serializer_class = VendorProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsVendor]
    
    
    @cached_property
    def profile(self):
        user = self.request.user
        profile, _ = Userprofile.objects.get_or_create(user=user)
        return profile
    
    @swagger_auto_schema(
        operation_summary="Retrieve Vendor Profile",
        operation_description="""
        - Fetches the authenticated vendor's profile.
        - If the profile doesn't exist, it is automatically created.
        """,
        responses={
            200: openapi.Response(
                "Vendor profile retrieved successfully",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "business_name": openapi.Schema(type=openapi.TYPE_STRING),
                                "business_address": openapi.Schema(type=openapi.TYPE_STRING),
                                "phone_number": openapi.Schema(type=openapi.TYPE_STRING),
                                "is_verified": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            }
                        )
                    }
                )
            ),
            400: openapi.Response(
                "Error Response",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "error": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
        }
    )
    def get(self, request):
        serializer = self.serializer_class(self.profile)
        return Response(
            {"success": True, "message": serializer.data},
            status=status.HTTP_200_OK
        )
        
    @swagger_auto_schema(
        operation_description="Update vendor profile and user details",
        request_body=VendorProfileSerializer,
        responses={200: "Vendor profile updated successfully", 400: "Invalid data"}
    )
    @transaction.atomic
    def patch(self, request):
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


class CategoryView(GenericAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    
    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return  [permissions.IsAuthenticated(), permissions.IsAdminUser()]
    
    
    @swagger_auto_schema(
        operation_summary="Retrieve All Categories",
        operation_description="""
        - Fetches a list of all available categories.
        - This endpoint is accessible to **everyone** (no authentication required).
        """,
        responses={
            200: openapi.Response(
                "Categories retrieved successfully",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "data": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "title": openapi.Schema(type=openapi.TYPE_STRING),
                                }
                            )
                        )
                    }
                )
            ),
            400: openapi.Response(
                "Error Response",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "error": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
        }
    )
    
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
    
    @swagger_auto_schema(
        operation_summary="Create a New Category",
        operation_description="""
        - Creates a new category (admin only).
        - If a category with the same title (case insensitive) already exists, it returns an error.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "title": openapi.Schema(type=openapi.TYPE_STRING, description="Category title"),
            },
            required=["title"]
        ),
        responses={
            201: openapi.Response(
                "Category created successfully",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "title": openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        )
                    }
                )
            ),
            400: openapi.Response(
                "Error Response",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
        }
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
    queryset = Category.objects.all()
    
    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            raise Http404
    
    @swagger_auto_schema(
        operation_summary="Retrieve a Single Category",
        operation_description="""
        - Retrieves details of a single category by ID.
        - Only **admin users** can access this endpoint.
        """,
        responses={
            200: openapi.Response(
                "Category retrieved successfully",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "title": openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        )
                    }
                )
            ),
            404: openapi.Response("Category not found"),
        }
    )
    
    def get(self, request, pk):
        category = self.get_object(pk=pk)
        serializer = CategorySerializer(category)
        return Response(
            {
                "success": True,
                "message": serializer.data
            }
        )
    
    @swagger_auto_schema(
        operation_summary="Update a Category (Partial)",
        operation_description="""
        - Updates a category's details (title).
        - **Only admins** can perform this action.
        - Supports partial updates (PATCH).
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "title": openapi.Schema(type=openapi.TYPE_STRING, description="Updated category title"),
            },
        ),
        responses={
            200: openapi.Response(
                "Category updated successfully",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "title": openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        )
                    }
                )
            ),
            400: openapi.Response("Validation error"),
            404: openapi.Response("Category not found"),
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
    
    @swagger_auto_schema(
        operation_summary="Delete a Category",
        operation_description="""
        - Deletes a category by ID.
        - **Only admins** can delete categories.
        - This action is irreversible.
        """,
        responses={
            204: openapi.Response("Category deleted successfully"),
            404: openapi.Response("Category not found"),
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
        return  [permissions.IsAuthenticated(), IsVendor()]
    
    @swagger_auto_schema(
        operation_summary="Retrieve a list of products",
        operation_description="""
        - Retrieves all products with optional filters.
        - Supports pagination.
        - Anyone can access this endpoint.
        """,
        manual_parameters=[
            openapi.Parameter("name", openapi.IN_QUERY, description="Filter by product name", type=openapi.TYPE_STRING),
            openapi.Parameter("category", openapi.IN_QUERY, description="Filter by category name", type=openapi.TYPE_STRING),
            openapi.Parameter("min_price", openapi.IN_QUERY, description="Filter products with price greater than or equal to this value", type=openapi.TYPE_NUMBER),
            openapi.Parameter("max_price", openapi.IN_QUERY, description="Filter products with price less than or equal to this value", type=openapi.TYPE_NUMBER),
        ],
        responses={
            200: openapi.Response(
                "Products retrieved successfully",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "data": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT)),
                    },
                ),
            ),
            400: openapi.Response("Invalid request parameters"),
        },
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
    
    @swagger_auto_schema(
        operation_summary="Create a new product",
        operation_description="""
        - Creates a new product (only accessible to authenticated vendors).
        - Requires valid product details in the request body.
        """,
        request_body=ProductSerializer,
        responses={
            201: openapi.Response(
                "Product created successfully",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "data": openapi.Schema(type=openapi.TYPE_OBJECT),
                    },
                ),
            ),
            400: openapi.Response(
                "Invalid data",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "errors": openapi.Schema(type=openapi.TYPE_OBJECT),
                    },
                ),
            ),
        },
    )
    
    @transaction.atomic
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Product created successfully",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                "success": False,
                "message": "Failed to create product",
                "errors": serializer.errors 
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
        return [permissions.IsAuthenticated(), IsVendor()]
    
    def get_object(self, pk, check_owner=False):
        """Retrieve product, and optionally enforce ownership check"""
        try:
            product = Product.objects.get(pk=pk)
            if check_owner and product.vendor != self.request.user:
                raise PermissionDenied("You do not have permission to modify this product.")
            return product
        except Product.DoesNotExist:
            raise Http404
    
    @swagger_auto_schema(
        operation_summary="Retrieve a single product",
        operation_description="Returns product details based on its ID. Accessible to everyone.",
        responses={
            200: openapi.Response(
                "Product retrieved successfully",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_OBJECT),
                    },
                ),
            ),
            404: "Product not found",
        },
    )
    
    def get(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(
            {
                "success": True,
                "message": serializer.data
            }
        )
    
    @swagger_auto_schema(
        operation_summary="Update a product",
        operation_description="Only the product owner (vendor) can update the product.",
        request_body=ProductSerializer,
        responses={
            200: "Product updated successfully",
            400: "Invalid request data",
            403: "Permission denied",
            404: "Product not found",
        },
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
    
    @swagger_auto_schema(
        operation_summary="Delete a product",
        operation_description="Only the product owner (vendor) can delete the product.",
        responses={
            204: "Product deleted successfully",
            403: "Permission denied",
            404: "Product not found",
        },
    )
    
    @transaction.atomic
    def delete(self, request, pk):
        product = self.get_object(pk, check_owner=True)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class ProductImageUploadView(GenericAPIView):
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticated, IsVendor]
    parser_classes = [MultiPartParser, FormParser]  

    @swagger_auto_schema(
        operation_summary="Upload images for a product",
        operation_description="Allows vendors to upload up to 5 images per product.",
        manual_parameters=[
            openapi.Parameter(
                name="image",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                description="Multiple images for the product",
                required=True,
            ),
            openapi.Parameter(
                name="product_id",
                in_=openapi.IN_PATH,
                description="ID of the product to upload images for",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response("Images uploaded successfully"),
            400: "Invalid request or image limit exceeded",
            403: "Permission denied",
            404: "Product not found",
        },
    )

    
    @transaction.atomic
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