from django.db import models


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
    duration = models.FloatField(null=True, verbose_name='Duration')
    protocol = models.CharField(
        blank=True,
        max_length=3,
        choices=PROTOCOL_CHOICES,
        verbose_name='Protocol',
    )
    jitter = models.FloatField(null=True, verbose_name='Jitter')
    asn_cc = models.CharField(blank=True, max_length=32, verbose_name='ASN Country Code')
    asn_desc = models.CharField(blank=True, max_length=32, verbose_name='ASN Description')
    packets = models.IntegerField(null=True, verbose_name='Packets Total')
    lost = models.IntegerField(null=True, verbose_name='Packets Lost')
    json = models.JSONField()
    version = models.CharField(blank=True, max_length=32, verbose_name='Iperf3 Version')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} ({}) - {}'.format(self.ip, self.name, self.bps_human)

    class Meta:
        verbose_name = 'SpeedTest'
        verbose_name_plural = 'SpeedTests'

    def get_type(self):
        return 'Download' if self.reverse else 'Upload'
