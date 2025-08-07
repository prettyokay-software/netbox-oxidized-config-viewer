from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel

class OxidizedConfigViewer(NetBoxModel):
    name = models.CharField(
        max_length=100,
        unique=True
    )
    last_changed = models.DateTimeField(
        blank=True,
        null=True
    )
    last_backup = models.DateTimeField(
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=50
    )

    class Meta:
        ordering = ('name',)

    def get_absolute_url(self):
        return reverse('plugins:netbox_oxidized_config_viewer:oxidizedconfigviewer', args=[self.pk])

    def __str__(self):
        return self.name
