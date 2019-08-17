from datetime import datetime

from django.db import models


class Information(models.Model):
    ip = models.CharField(max_length=32)
    public_key = models.CharField(max_length=256)
    random = models.CharField(max_length=256)
    time_request = models.CharField(max_length=12)
    date_request = models.CharField(max_length=12, default=datetime.now().strftime("%d-%m-%Y"))
    counter = models.IntegerField(default=1)


class Token(models.Model):
    public_key = models.CharField(max_length=256)
    token = models.CharField(max_length=256)
    time_request = models.CharField(max_length=12)
    date_request = models.CharField(max_length=12, default=datetime.now().strftime("%d-%m-%Y"))
    counter = models.IntegerField(default=1)
