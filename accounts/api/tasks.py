from celery import shared_task
from django.utils import timezone

from accounts.models import UserSubscription



@shared_task
def deactivate_expired_subscriptions():
    # Get expired subscriptions
    expired_subscriptions = UserSubscription.objects.filter(end_date__lt=timezone.now(), active=True)

    # Deactivate expired subscriptions
    expired_subscriptions.update(active=False)
    
    return expired_subscriptions.count()



@shared_task
def send_notification_to_admin(count):
    # Send a notification with the count of deactivated subscriptions
    print(f"{count} subscriptions have been deactivated.")
    return "Notification sent."
