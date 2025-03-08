from django.urls import path, include
from authentication.views import CustomerSignUpView, VendorSignUpView, VerifyAccount, RequestNewOTP, LoginView, LogoutView, PasswordResetRequestView, PasswordResetView, UploadProfilePicView


urlpatterns = [
    # Auth
    path("auth/signup/customer/", CustomerSignUpView.as_view()),
    path("auth/signup/vendor/", VendorSignUpView.as_view()),
    path("auth/signup/verify_acount/", VerifyAccount.as_view()),
    path("auth/request_otp/", RequestNewOTP.as_view()),
    path("auth/login/", LoginView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
    path("auth/forgot_password/", PasswordResetRequestView.as_view()),
    path("auth/reset_password/", PasswordResetView.as_view()),
    
    path("upload/profile_pic/", UploadProfilePicView.as_view()),
    
    
    
    
    path("vendor/", include("vendor.urls"))
]