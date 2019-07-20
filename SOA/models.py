from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.db import models


class Address(models.Model):
    city = models.CharField(max_length = 15)
    street = models.CharField(max_length = 15)
    alley = models.CharField(max_length = 15)
    postal_code = models.CharField(max_length = 10)
    plaque = models.CharField(max_length = 10)
    phone = models.CharField(max_length = 11)
    fax = models.CharField(max_length = 11)
    details = models.CharField(max_length = 100)


class User(AbstractUser):
    phone = models.CharField(max_length = 11)
    personnel_code = models.CharField(max_length = 15)
    in_place = models.BooleanField(default = False)
    address = models.ForeignKey(Address, on_delete = models.CASCADE, null=True)


class License(models.Model):
    # boolean Fields for features
    expire_date = models.DateField()


class Arash(models.Model):
    private_key = models.CharField(max_length = 256)
    public_key = models.CharField(max_length = 256)
    serial_number = models.CharField(max_length = 16)
    license = models.ForeignKey(License, on_delete = models.CASCADE)
    version = models.CharField(max_length = 10)


class Company(models.Model):
    name = models.CharField(max_length = 10)
    arash = models.ForeignKey(Arash, on_delete = models.CASCADE)
    address = models.ForeignKey(Address, on_delete = models.CASCADE)
    email = models.EmailField(max_length = 25)
