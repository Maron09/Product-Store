from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404, GenericAPIView
from rest_framework.parsers import JSONParser
from .models import Cart
from .serializers import CartSerializer
from authentication.permissions import IsCustomer
from rest_framework import status, permissions
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



class CartView(GenericAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]
    queryset = Cart.objects.all()
    
    
    def get(self, request):
        cart_items = Cart.objects.filter(customer=request.user)
        serializer = self.serializer_class(cart_items, many=True)
        return Response(
            {
                "success": True,
                "message": "Cart Items",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    
    @transaction.atomic
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(customer=request.user)
            return Response(
                {
                    "success": True,
                    "message": "Product Added to cart",
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



class CartDetailView(GenericAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]
    queryset = Cart.objects.all()
    
    
    def get_queryset(self):
        """Ensure users can only access their own cart items"""
        return Cart.objects.filter(customer=self.request.user)
    
    def get_object(self, cart_id):
        """Fetch a single cart item belonging to the user"""
        return get_object_or_404(Cart, id=cart_id, customer=self.request.user)
    
    def get(self, request, cart_id):
        """Retrieve details of a specific cart item"""
        cart_item = self.get_object(cart_id)
        serializer = self.serializer_class(cart_item)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK
        )
    
    @transaction.atomic
    def patch(self, request, cart_id):
        cart_item = self.get_object(cart_id)
        serializer = self.serializer_class(cart_item, data=request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save(customer=request.user)
            return Response(
                {
                    "success": True,
                    "message": "Cart Quantity Updated",
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
    
    @transaction.atomic
    def delete(self, request, cart_id):
        cart_item = self.get_object(cart_id)
        cart_item.delete()
        return Response(
            {
                "success": True,
                "message": "Item removed from cart"
            },
            status=status.HTTP_204_NO_CONTENT
        )