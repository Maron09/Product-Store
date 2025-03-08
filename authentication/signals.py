from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import User, EmailOTP, Userprofile, PasswordResetToken
from .utils import send_otp
from django.conf import settings
from django.core.mail import send_mail


@receiver(post_save, sender=User)
def create_otp(sender, instance, created, **kwargs):
    """Generate OTP and send email after user signup"""
    if created:
        otp, _ = EmailOTP.objects.get_or_create(user=instance)
        otp.generate_otp()
        send_otp(instance.email, otp.code)


@receiver(post_save, sender=User)
def post_save_created_profile(sender, instance, created, **kwargs):
    if created:
        Userprofile.objects.create(user=instance)
    else:
        try:
            profile = Userprofile.objects.get(user=instance)
            profile.save()
        except:
            Userprofile.objects.create(user=instance)


@receiver(pre_save, sender=User)
def pre_save_profile(sender, instance, **kwargs):
    print(instance.email)


@receiver(post_save, sender=PasswordResetToken)
def send_password_reset_email(sender, instance, created, **kwargs):
    if created:
        base_url = getattr(settings, "SITE_URL", "http://127.0.0.1:8001")
        reset_link = f"{base_url}/api/reset_password/{instance.token}"
        send_mail(
            "Password Reset Request",
            f"Click the link to reset your password: {reset_link}",
            "noreply@example.com",
            [instance.user.email],
            fail_silently=False,
        )