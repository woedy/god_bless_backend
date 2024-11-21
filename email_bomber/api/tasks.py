# myapp/tasks.py
import random
import string
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_email_task(recipient_email, subject, message):
    send_mail(subject, message, 'your_email@gmail.com', [recipient_email])

def generate_random_message():
    length = random.randint(10, 50)  # Random length for the message
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@shared_task
def send_random_emails(recipient_email, count=50):
    for _ in range(count):
        subject = "Random Subject"
        message = generate_random_message()
        send_email_task.delay(recipient_email, subject, message)
