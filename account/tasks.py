from django.conf import settings

from webvirtcloud.celery import app
from webvirtcloud.email import send_email


@app.task
def email_confirm_register(recipient, hash):
    subject = "WebVirtCloud confirm registration"
    confirm_url = f"{settings.CLIENT_URL}/confirm-email/{hash}/"
    context = {"confirm_url": confirm_url, "site_url": settings.SITE_URL}
    send_email(subject, recipient, context, "email/account-registration-confirm.html")
