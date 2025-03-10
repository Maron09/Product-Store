from django.urls import path
from .views import CustomerProfileView, WishlistView



urlpatterns = [
    path("profile/", CustomerProfileView.as_view()),
    path("wishlist/", WishlistView.as_view())
]