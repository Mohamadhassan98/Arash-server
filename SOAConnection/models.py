from datetime import datetime

from django.db import models
from mongoengine import *

connect('localhost')


class Information(models.Model):
    ip = models.CharField(max_length=32)
    public_key = models.TextField(max_length=2048)
    random = models.CharField(max_length=256)
    time_request = models.CharField(max_length=12)
    date_request = models.CharField(max_length=12, default=datetime.now().strftime("%d-%m-%Y"))
    counter = models.IntegerField(default=1)


class Token(models.Model):
    public_key = models.TextField(max_length=2048)
    token = models.CharField(max_length=256)
    time_request = models.CharField(max_length=12)
    date_request = models.CharField(max_length=12, default=datetime.now().strftime("%d-%m-%Y"))
    counter = models.IntegerField(default=1)


class ArashVersion(models.Model):
    version = models.CharField(max_length=15)
    time = models.DateField()
    file = models.CharField(max_length=256)


class AliveRequest(Document):
    date_time = models.DateTimeField(default=datetime.now())
    public_key = models.CharField(max_length=256)
