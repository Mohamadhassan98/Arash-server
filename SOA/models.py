# from django.contrib.auth.base_user import AbstractBaseUser
# from django.contrib.auth.models import AbstractUser
# from django.db import models
#
#
# class User(AbstractUser):
#     address = models.OneToOneField(Address, on_delete=models.CASCADE, null=True, related_name='user')
from django.contrib.auth.models import AbstractUser
from django.db import models


class Address(models.Model):
    city = models.CharField(max_length=15)
    street = models.CharField(max_length=15)
    alley = models.CharField(max_length=15, null=True)
    postal_code = models.CharField(max_length=10)
    plaque = models.CharField(max_length=10)
    phone = models.CharField(max_length=11)
    fax = models.CharField(max_length=11, null=True)
    details = models.CharField(max_length=100, null=True)

    class Meta:
        verbose_name_plural = 'addresses'


class User(AbstractUser):
    phone = models.CharField(max_length=11)
    personnel_code = models.CharField(max_length=15)
    in_place = models.BooleanField(default=False)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='users', null=True)


class License(models.Model):
    # boolean Fields for features
    expire_date = models.DateField()


class Company(models.Model):
    name = models.CharField(max_length=10)
    address = models.OneToOneField(Address, on_delete=models.CASCADE, related_name='company')
    email = models.EmailField(max_length=25)

    class Meta:
        verbose_name_plural = 'companies'


class Arash(models.Model):
    private_key = models.CharField(max_length=256)
    public_key = models.CharField(max_length=256)
    serial_number = models.CharField(max_length=16)
    license = models.OneToOneField(License, on_delete=models.CASCADE, related_name='arash')
    version = models.CharField(max_length=10)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='arashes')

    class Meta:
        verbose_name_plural = 'arashes'


class Request(models.Model):
    problem = models.TextField(max_length=256)
    solve = models.TextField(max_length=256)
    request_date = models.DateTimeField()
    solve_date = models.DateTimeField()
    arash = models.ForeignKey(Arash, on_delete=models.CASCADE, related_name='requests')
    user = models.ManyToManyField(User, related_name='requests')
