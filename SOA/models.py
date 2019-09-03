import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models


class Address(models.Model):
    city = models.CharField(max_length=15)
    street = models.CharField(max_length=15)
    alley = models.CharField(max_length=15, null=True, blank=True)
    postal_code = models.CharField(max_length=10)
    plaque = models.CharField(max_length=10)
    telephone = models.CharField(max_length=11)
    fax = models.CharField(max_length=11, null=True, blank=True)
    details = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'addresses'


def get_user_profile_path(instance, filename: str):
    return str(instance.username) + '.' + filename.split('.')[-1]


class User(AbstractUser):
    phone = models.CharField(max_length=11)
    personnel_code = models.CharField(max_length=15)
    in_place = models.BooleanField(default=False)
    address = models.OneToOneField(Address, on_delete=models.CASCADE, related_name='users', null=True)
    profile_pic = models.ImageField(upload_to=get_user_profile_path, default='default.png')


class Company(models.Model):
    name = models.CharField(max_length=10)
    address = models.OneToOneField(Address, on_delete=models.CASCADE, related_name='company')
    email = models.EmailField(max_length=25)

    # TODO merge Company_code

    class Meta:
        verbose_name_plural = 'companies'


class Arash(models.Model):
    STATUS = (
        ('alv', 'Alive'),
        ('dead', 'Dead'),
        ('dng', 'Dangerous')
    )

    features = ['features']
    public_key = models.TextField(max_length=2048)
    serial_number = models.CharField(max_length=16)
    license = models.CharField(max_length=256)
    expire_date = models.DateField()
    version = models.CharField(max_length=10)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='arashes')
    purchase_date = models.DateField(default=datetime.date.today)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=4, choices=STATUS, default='dead')

    def modify_active(self):
        if self.is_active:
            if datetime.date.today() > self.expire_date:
                self.is_active = False
                self.save()

    def modify_status(self, last_request):
        mins = (datetime.datetime.now() - last_request).total_seconds() // 3600
        if mins > 30:
            self.status = 'dead'
        elif mins > 5:
            self.status = 'dng'
        else:
            self.status = 'alv'
        self.save()

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
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    details = models.TextField()

    # noinspection DuplicatedCode, PyProtectedMember
    def edit_fields(self, old_obj, new_obj):
        fields = 'field names: '
        for field in old_obj._meta.fields:
            fields += '%s, ' % field.name
        fields = fields[:-2]
        fields += '; old values: '
        for field in old_obj._meta.fields:
            fields += '%s, ' % getattr(old_obj, field.name)
        fields = fields[:-2]
        fields += '; new values: '
        for field in old_obj._meta.fields:
            fields += '%s, ' % getattr(new_obj, field.name)
        fields = fields[:-2]
        self.details = fields

    # noinspection DuplicatedCode, PyProtectedMember
    def add_or_remove_fields(self, obj):
        fields = 'field names: '
        for field in obj._meta.fields:
            fields += '%s, ' % field.name
        fields = fields[:-2]
        fields += '; values: '
        for field in obj._meta.fields:
            fields += '%s, ' % getattr(obj, field.name)
        fields = fields[:-2]
        fields += ';'
        self.details = fields
