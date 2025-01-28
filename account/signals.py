from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
import random
from django.core.mail import send_mail
from account.models import UserProfile, EmailCode


@receiver(post_save, sender=UserProfile)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.email:
        email_code = EmailCode(mail_code=random.randint(1000, 9999), profile=instance)
        email_code.save()
        link = f"{settings.BACKEND_SERVER_BASE_URL}/account/verify_signup_email/{instance.email}/{email_code.mail_code}"
        print(link)
        send_mail(
            "Verify your account",
            f"Click the link to verify your account:{link}",
            "admin@example.com",
            [instance.email],
            fail_silently=False,
        )
