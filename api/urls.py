from django.urls import path, include
from authentication.views import CustomerSignUpView, VendorSignUpView, VerifyAccount, RequestNewOTP, LoginView, LogoutView, PasswordResetRequestView, PasswordResetView, UploadProfilePicView
from vendor.views import CategoryView, CategoryDetailView, ProductView


urlpatterns = [
    # Auth
    path("auth/signup/customer/", CustomerSignUpView.as_view()),
    path("auth/signup/vendor/", VendorSignUpView.as_view()),
    path("auth/verify_acount/", VerifyAccount.as_view()),
    path("auth/request_otp/", RequestNewOTP.as_view()),
    path("auth/login/", LoginView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
    path("auth/forgot_password/", PasswordResetRequestView.as_view()),
    path("auth/reset_password/", PasswordResetView.as_view()),
    
    path("upload/profile_pic/", UploadProfilePicView.as_view()),
    # Category
    path("category/", CategoryView.as_view()),
    path("category/<int:pk>/", CategoryDetailView.as_view()),
    
    # Product
    path("products/", ProductView.as_view()),
    
    # Vendor
    path("vendor/", include("vendor.urls")),
    
    # Customer
    path('customer/', include('customer.urls'))
]