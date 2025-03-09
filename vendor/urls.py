from django.urls import path
from .views import VendorProfileView, ProductDetailView, CategoryView, ProductImageUploadView


urlpatterns = [
    path("profile/", VendorProfileView.as_view()),
    path("product/<int:pk>/", ProductDetailView.as_view()),
    path("product/upload/<int:product_id>/", ProductImageUploadView.as_view())
]