from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .tasks import clear_home_cache, delete_discord_webhook, send_success_message
from .models import SpeedTest, Webhooks


@receiver(post_save, sender=SpeedTest)
@receiver(post_delete, sender=SpeedTest)
def clear_home_cache_signal(sender, instance, **kwargs):
    clear_home_cache.delay()


@receiver(post_delete, sender=Webhooks)
def delete_discord_webhook_signal(sender, instance, **kwargs):
    delete_discord_webhook.delay(instance.url)


@receiver(post_save, sender=Webhooks)
def send_success_message_signal(sender, instance, **kwargs):
    if 'created' in kwargs and kwargs['created']:
        send_success_message.delay(instance.id)
