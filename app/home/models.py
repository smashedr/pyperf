from django.conf import settings
from django.db import models
from django.urls import reverse
from oauth.models import CustomUser


class SpeedTest(models.Model):
    PROTOCOL_CHOICES = [
        ('TCP', 'TCP'),
        ('UDP', 'UDP'),
    ]
    id = models.AutoField(primary_key=True)
    ip = models.CharField(blank=True, max_length=15, verbose_name='IP Address')
    name = models.CharField(blank=True, max_length=128, verbose_name='Host name')
    reverse = models.BooleanField(null=True, verbose_name='Reverse (Download)')
    bps = models.FloatField(null=True, verbose_name='BPS')
    bps_human = models.CharField(blank=True, max_length=32, verbose_name='BPS Human')
    bytes = models.IntegerField(null=True, verbose_name='Bytes')
    bytes_human = models.CharField(blank=True, max_length=32, verbose_name='Bytes Human')
    duration = models.IntegerField(null=True, verbose_name='Duration')
    protocol = models.CharField(
        blank=True,
        max_length=3,
        choices=PROTOCOL_CHOICES,
        verbose_name='Protocol',
    )
    jitter = models.FloatField(null=True, verbose_name='Jitter')
    ip_cc = models.CharField(blank=True, max_length=2, verbose_name='IP Country Code')
    ip_country = models.CharField(blank=True, max_length=32, verbose_name='IP Country Name')
    ip_rc = models.CharField(blank=True, max_length=32, verbose_name='IP Region Code')
    ip_region = models.CharField(blank=True, max_length=32, verbose_name='IP Region Name')
    ip_city = models.CharField(blank=True, max_length=32, verbose_name='IP City')
    ip_org = models.CharField(blank=True, max_length=32, verbose_name='IP Organization')
    ip_lat = models.FloatField(null=True, verbose_name='IP Latitude')
    ip_lon = models.FloatField(null=True, verbose_name='IP Longitude')
    packets = models.IntegerField(null=True, verbose_name='Packets Total')
    lost = models.IntegerField(null=True, verbose_name='Packets Lost')
    json = models.JSONField()
    version = models.CharField(blank=True, max_length=32, verbose_name='Iperf3 Version')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}: {} ({})'.format(self.pk, self.name, self.bps_human)

    class Meta:
        verbose_name = 'Speed Test'
        verbose_name_plural = 'Speed Tests'
        get_latest_by = 'pk'

    def get_type(self):
        return 'Download' if self.reverse else 'Upload'

    def get_result_url(self):
        url = reverse('home:result', kwargs={'pk': self.pk})
        return f'{settings.SITE_URL}{url}'

    def get_image_url(self):
        url = reverse('home:image', kwargs={'pk': self.pk})
        return f'{settings.SITE_URL}{url}'

    def get_graph_url(self):
        url = reverse('home:graph', kwargs={'pk': self.pk})
        return f'{settings.SITE_URL}{url}'

    def get_map_url(self):
        url = reverse('home:map', kwargs={'pk': self.pk})
        return f'{settings.SITE_URL}{url}'


class Webhooks(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.URLField(unique=True, verbose_name='Webhook URL')
    hook_id = models.CharField(max_length=32, blank=True, null=True)
    guild_id = models.CharField(max_length=32, blank=True, null=True)
    channel_id = models.CharField(max_length=32, blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return '{}: {} ({})'.format(self.id, self.hook_id, self.owner.first_name)

    class Meta:
        verbose_name = 'Webhook'
        verbose_name_plural = 'Webhooks'
