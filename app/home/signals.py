from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .tasks import clear_home_cache
from .models import SpeedTest


@receiver(post_save, sender=SpeedTest)
@receiver(post_delete, sender=SpeedTest)
def clear_cache(sender, instance, **kwargs):
    clear_home_cache.delay()
