# myapp/views.py
from django.http import HttpResponse
from .tasks import send_random_emails

def send_bulk_emails(request):
    recipient_email = 'recipient@example.com'
    send_random_emails.delay(recipient_email)  # Trigger the task asynchronously
    return HttpResponse("Sent 50 emails!")
