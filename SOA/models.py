import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models


class Address(models.Model):
    city = models.CharField(max_length=15)
    street = models.CharField(max_length=15)
    alley = models.CharField(max_length=15, null=True)
    postal_code = models.CharField(max_length=10)
    plaque = models.CharField(max_length=10)
    tel_phone = models.CharField(max_length=11)
    fax = models.CharField(max_length=11, null=True)
    details = models.CharField(max_length=100, null=True)

    class Meta:
        verbose_name_plural = 'addresses'


class User(AbstractUser):
    phone = models.CharField(max_length=11)
    personnel_code = models.CharField(max_length=15)
    in_place = models.BooleanField(default=False)
    address = models.OneToOneField(Address, on_delete=models.CASCADE, related_name='users', null=True)
    user_status = [
        ('ad', 'admin'),
        ('ma', 'master')

    ]
    status = models.CharField(max_length=2, choices=user_status, default='ad')


class Company(models.Model):
    name = models.CharField(max_length=10)
    address = models.OneToOneField(Address, on_delete=models.CASCADE, related_name='company')
    email = models.EmailField(max_length=25)

    class Meta:
        verbose_name_plural = 'companies'


class Arash(models.Model):
    features = ['features']
    public_key = models.CharField(max_length=256)
    serial_number = models.CharField(max_length=16)
    license = models.CharField(max_length=256)
    expire_date = models.DateField()
    version = models.CharField(max_length=10)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='arashes')
    purchase_date = models.DateField(default=datetime.date.today)

    @property
    def is_active(self):
        return datetime.date.today() < self.expire_date

    class Meta:
        verbose_name_plural = 'arashes'


class Request(models.Model):
    problem = models.TextField(max_length=256)
    solve = models.TextField(max_length=256)
    request_date = models.DateTimeField()
    solve_date = models.DateTimeField()
    arash = models.ForeignKey(Arash, on_delete=models.CASCADE, related_name='requests')
    users = models.ManyToManyField(User, related_name='requests')


class Log(models.Model):
    OPERATIONS = (
        ('+', 'Add'),
        ('-', 'Remove'),
        ('*', 'Update')
    )

    operation = models.CharField(max_length=1, choices=OPERATIONS)
    operand = models.CharField(max_length=20)
    operand_object = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fields = models.TextField(null=True)

    def edit_fields(self, old, new):
        fields = 'field names: '
        for field_name, _ in new.items():
            fields += '%s, ' % field_name
        fields = fields[:-2]
        fields += '; old values: '
        for field in old:
            fields += '%s, ' % field
        fields = fields[:-2]
        fields += '; new values: '
        for _, field in new.items():
            fields += '%s, ' % field
        fields = fields[:-2]
        fields += ';'
        self.fields = fields
