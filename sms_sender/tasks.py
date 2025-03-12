# tasks.py
from celery import shared_task
from time import sleep
from email.mime.text import MIMEText
import smtplib
import ssl

@shared_task(bind=True)
def send_bulk_sms_via_email_task(self, numbers, sender_name: str, subject: str, message: str, smtps, provider: str, delay_seconds: int = 1):
    smtp_index = 0
    total = len(numbers)
    
    for index, number in enumerate(numbers):
        # Update task progress
        progress = (index + 1) / total * 100  # Percentage of task completed
        self.update_state(state='PROGRESS', meta={'progress': progress})

        smtp = smtps[smtp_index]
        sender_email = smtp.username
        email_password = smtp.password
        receiver_email = format_provider_email_address(number, provider)

        # Create the email message
        email_message = MIMEText(message)
        email_message["Subject"] = subject
        email_message["from"] = sender_name
        email_message["To"] = receiver_email

        try:
            with smtplib.SMTP_SSL(smtp.host, smtp.port, context=ssl.create_default_context()) as email:
                email.login(sender_email, email_password)
                email.sendmail(sender_email, receiver_email, email_message.as_string())
        except smtplib.SMTPException as e:
            print(f"Failed to send email: {e}")

        # Alternate to the next SMTP configuration
        smtp_index = (smtp_index + 1) % len(smtps)

        # Introduce a delay between sending each email
        sleep(delay_seconds)

    return {'status': 'Task Completed'}
