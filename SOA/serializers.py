import re

from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import *


def validate_phone_numbers(phone):
    regex = r'^0\d{10}'
    if not re.search(regex, phone):
        raise ValidationError('phone must be an 11 digit number')
    return phone


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

    CITIES = (
        'اصفهان', 'تهران', 'شیراز',
    )

    def validate_city(self, city):
        if city not in self.CITIES:
            raise ValidationError('Not a valid City.')
        return city

    def validate_postal_code(self, postal_code):
        regex = r'\d{10}'
        if not re.search(regex, postal_code):
            raise ValidationError('postal_code must be a ten digit number')
        return postal_code

    def validate_phone(self, phone):
        return validate_phone_numbers(phone)

    def validate_fax(self, fax):
        return validate_phone_numbers(fax)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('is_superuser', 'is_staff', 'date_joined', 'last_login', 'groups', 'user_permissions', 'is_active')
        depth = 1

    def create(self, validated_data) -> User:
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        return User.objects.create_user(username=username, password=password, **validated_data)

    def validate_phone(self, phone):
        return validate_phone_numbers(phone)


class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = License
        fields = '__all__'

    def validate_expire_date(self, expire_date):
        if expire_date < now:
            raise ValidationError('expire_date should be in the future')
        return expire_date


class ArashSerializer(serializers.ModelSerializer):
    class Meta:
        model = Arash
        fields = '__all__'


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        exclude = ('address',)


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        exclude = ('arash', 'users')

    def create(self, validated_data) -> Request:
        pass
