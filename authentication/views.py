
from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView
from .serializers import CustomerSignUpSerializer, VendorSignUpSerializer, RequestNewOTPSerializer, LoginSerializer, LogoutSerializer, PasswordRestRequestSerializer, PasswordResetSerializer
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from .models import User, EmailOTP
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .utils import send_otp
from rest_framework import status, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken


class CustomerSignUpView(GenericAPIView):
    """
    Registers A Customer:
    - Creates a new customer account.
    - Sends an OTP for account verification.
    - If the email exists but the user is not active, a new OTP is sent.
    - If the email exists and the user is active, registration is blocked.
    """
    serializer_class = CustomerSignUpSerializer

    @swagger_auto_schema(
        operation_summary="Customer Registration",
        operation_description="""
        - Registers a new customer and sends an OTP for account verification.
        - If the email already exists but the customer is **not active**, a new OTP is sent.
        - If the email already exists and the customer is **active**, registration is blocked.
        """,
        request_body=CustomerSignUpSerializer,
        responses={
            201: openapi.Response(
                "Customer registered successfully",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "email": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                                "first_name": openapi.Schema(type=openapi.TYPE_STRING),
                                "last_name": openapi.Schema(type=openapi.TYPE_STRING),
                                "phone_number": openapi.Schema(type=openapi.TYPE_STRING),
                                "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            }
                        )
                    }
                )
            ),
            200: openapi.Response(
                "Resent OTP",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING)
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
    @transaction.atomic
    def post(self, request):
        email = request.data.get("email")
        existing_user = User.objects.filter(email=email).first()

        if existing_user:
            if not existing_user.is_active:
                otp, _ = EmailOTP.objects.get_or_create(user=existing_user)
                otp.generate_otp()
                return Response({"success": True, "message": "User already registered but not active. OTP sent."}, status=status.HTTP_200_OK)
            return Response({"success": False, "error": "User with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"success": True, "message": "Customer registered. Check email for OTP.", "data": CustomerSignUpSerializer(user).data}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class VendorSignUpView(GenericAPIView):
    """
    Registers a Vendor:
    - Creates a new vendor account.
    - Sends an OTP for account verification.
    - If the email exists but the user is not active, a new OTP is sent.
    - If the email exists and the user is active, registration is blocked.
    """
    serializer_class = VendorSignUpSerializer
    
    @swagger_auto_schema(
        operation_summary="Vendor Registration",
        operation_description="""
        - Registers a new vendor and sends an OTP for account verification.
        - If the email already exists but the vendor is **not active**, a new OTP is sent.
        - If the email already exists and the vendor is **active**, registration is blocked.
        """,
        request_body=VendorSignUpSerializer,
        responses={
            201: openapi.Response(
                "Vendor registered successfully",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "email": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                                "first_name": openapi.Schema(type=openapi.TYPE_STRING),
                                "last_name": openapi.Schema(type=openapi.TYPE_STRING),
                                "phone_number": openapi.Schema(type=openapi.TYPE_STRING),
                                "business_name": openapi.Schema(type=openapi.TYPE_STRING),
                                "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            }
                        )
                    }
                )
            ),
            200: openapi.Response(
                "Resent OTP",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING)
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
    @transaction.atomic
    def post(self, request):
        email = request.data.get("email")
        existing_user = User.objects.filter(email=email).first()

        if existing_user:
            if not existing_user.is_active:
                otp, _ = EmailOTP.objects.get_or_create(user=existing_user)
                otp.generate_otp()
                return Response({"success": True, "message": "User already registered but not active. OTP sent."}, status=status.HTTP_200_OK)
            return Response({"success": False, "error": "User with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"success": True, "message": "Vendor registered. Check email for OTP.", "data": VendorSignUpSerializer(user).data}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyAccount(GenericAPIView):
    """
    User Account Verification View:
    - Verifies a user's account using an OTP.
    - If the OTP is valid, the user's account is activated.
    - If the OTP is missing or incorrect, an appropriate error response is returned.
    """

    @swagger_auto_schema(
        operation_summary="Verify User Account",
        operation_description="""
        - Verifies a user's account by checking the provided OTP.
        - If the OTP is valid and not expired, the user's account is activated.
        - If the OTP is missing, expired, or incorrect, an appropriate error response is returned.
        - If the account is already active, an error response is returned.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "otp": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="One-Time Password (OTP) sent to the user's email"
                )
            },
            required=["otp"]
        ),
        responses={
            200: openapi.Response(
                "Account Verified Successfully",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(
                "Bad Request",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Possible messages: 'OTP not provided', 'OTP has expired', or 'Account already active'."
                        )
                    }
                )
            ),
            404: openapi.Response(
                "Not Found - Invalid OTP",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            500: openapi.Response(
                "Internal Server error",
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
        otp_code = request.data.get('otp')
        
        if not otp_code:
            return Response (
                {
                    "success": False,
                    "message": "OTP not Provided"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            user_code_obj = EmailOTP.objects.filter(code=otp_code).first()
            
            if not user_code_obj:
                return Response(
                    {
                        "success": False,
                        "message": "Invalid OTP"
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
                
            if not user_code_obj.is_valid():
                return Response(
                    {
                        "success": False,
                        "message": "OTP has expired"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            user = user_code_obj.user
            if not user.is_active:
                user.is_active = True
                user.save()
                user_code_obj.delete()
                return Response(
                    {
                        "success": True,
                        "message": "Account Verified Successfully"
                    },
                    status=status.HTTP_200_OK
                )
            return Response(
                {
                    "success": False,
                    "message": "Account already Active"
                }
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"An Error occurred: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RequestNewOTP(GenericAPIView):
    
    """
    API endpoint to request a new OTP if the previous one has expired.
    Users need to provide their registered email to receive a new OTP.
    """
    
    serializer_class = RequestNewOTPSerializer
    
    @swagger_auto_schema(
        operation_summary="Request New OTP",
        operation_description="""
        - Requests a new OTP for account verification.
        - The user must provide a registered email.
        - If the email is valid, a new OTP is sent.
        - If the email is missing or the user does not exist, an error response is returned.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description="Registered email address of the user"
                )
            },
            required=["email"]
        ),
        responses={
            200: openapi.Response(
                "OTP Sent Successfully",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(
                "Bad Request - Missing Email",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Possible message: 'Email is required to request a new OTP'."
                        )
                    }
                )
            ),
            404: openapi.Response(
                "Not Found - User Does Not Exist",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            500: openapi.Response(
                "Internal Server Error",
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
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data["email"]
        
        if not email:
            return Response (
                {
                    "success": False,
                    "message": "Email is required to request a new OTP"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
            
            EmailOTP.objects.filter(user=user).delete()
            
            otp = EmailOTP.objects.create(user=user)
            otp.generate_otp()
            send_otp(user.email, otp.code)
            return Response (
                {
                    "success": True,
                    "message": "A new OTP has been sent to your email"
                },
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "User with this email does not exist"
                },
                status=status.HTTP_404_NOT_FOUND
            )



class LoginView(GenericAPIView):
    
    """
    API endpoint for user authentication.
    """
    
    serializer_class = LoginSerializer
    
    @swagger_auto_schema(
        operation_summary="User Login",
        operation_description="""
        - Authenticates a user using email and password.
        - Returns access and refresh tokens upon successful login.
        - If credentials are incorrect or account is inactive, an error is returned.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description="User's registered email"
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_PASSWORD,
                    description="User's password"
                )
            },
            required=["email", "password"]
        ),
        responses={
            200: openapi.Response(
                "Login Successful",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "email": openapi.Schema(type=openapi.TYPE_STRING),
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "full_name": openapi.Schema(type=openapi.TYPE_STRING),
                                "access_token": openapi.Schema(type=openapi.TYPE_STRING),
                                "refresh_token": openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        )
                    }
                )
            ),
            400: openapi.Response(
                "Bad Request - Invalid Input",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Possible message: 'Invalid Credentials'."
                        )
                    }
                )
            ),
            401: openapi.Response(
                "Unauthorized - Account Not Active",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            500: openapi.Response(
                "Internal Server Error",
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
    
    def post(self, request):
        context = {"request": request}
        
        serializer = self.serializer_class(data=request.data, context=context)
        if serializer.is_valid():
            user = serializer.validated_data
            return Response(
                {
                    "success": True,
                    "message": "Login Successfull",
                    "data": user
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(GenericAPIView):
    
    """
    Logs out the user by blacklisting the provided refresh token.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    # authentication_classes = [JWTAuthentication]
    serializer_class = LogoutSerializer
    
    @swagger_auto_schema(
        operation_summary="User Logout",
        operation_description="""
        - Logs out the user by invalidating the refresh token.
        - Requires a valid refresh token to be sent in the request body.
        - If the refresh token is missing or invalid, an error is returned.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Valid refresh token required for logout"
                )
            },
            required=["refresh"]
        ),
        responses={
            200: openapi.Response(
                "Logout Successful",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, description="Logout Successful")
                    }
                )
            ),
            400: openapi.Response(
                "Bad Request - Missing or Invalid Refresh Token",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                    }
                )
            ),
        }
    )
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh = request.data.get("refresh")
            if not refresh:
                return Response(
                    {
                        "success":False,
                        "message": "Refresh token is required"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken(refresh)
            token.blacklist()
            
            return Response(
                {
                    "success": True,
                    "message": "Logout Successfull"
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"Error during logout, {str(e)}"
                },
                status=status.HTTP_400_BAD_REQUEST
            )



class PasswordResetRequestView(GenericAPIView):
    
    """
    Takes the users email and sends a token
    """
    
    serializer_class = PasswordRestRequestSerializer
    
    @swagger_auto_schema(
        operation_summary="Request Password Reset",
        operation_description="""
        - Users can request a password reset link.
        - The system verifies if the email exists and sends a password reset token.
        - If the email does not exist, an error is returned.
        """,
        request_body=PasswordRestRequestSerializer,
        responses={
            200: openapi.Response(
                "Password Reset Link Sent Successfully",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: openapi.Response(
                "Error Response",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
        }
    )
    
    @transaction.atomic
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Password Reset Link Sent To Email"
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                "success": False,
                "message": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )



class PasswordResetView(GenericAPIView):
    
    """
    Resets the user's password
    """
    
    serializer_class = PasswordResetSerializer
    
    @swagger_auto_schema(
        operation_summary="Reset Password",
        operation_description="""
        - Users can reset their password using the token received via email.
        - The system verifies if the token is valid and updates the password.
        - If the token is invalid or expired, an error is returned.
        """,
        request_body=PasswordResetSerializer,
        responses={
            200: openapi.Response(
                "Password Reset Successfully",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: openapi.Response(
                "Error Response",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
        }
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Password Reset Succesfully"
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                "success": False,
                "message": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )