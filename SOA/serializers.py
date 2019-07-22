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


# noinspection PyMethodMayBeStatic
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


# noinspection PyMethodMayBeStatic
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('is_superuser', 'is_staff', 'date_joined', 'last_login', 'groups', 'user_permissions', 'is_active')
        # depth = 1

    def create(self, validated_data) -> User:
        print(validated_data)
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        return User.objects.create_user(username=username, password=password, **validated_data)

    # def validate(self, attrs):
    #     print('attrs')
    #     print(attrs)
    #     return attrs

    def update(self, instance: User, validated_data) -> User:
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.personnel_code = validated_data.get('personnel_code', instance.personnel_code)
        instance.in_place = validated_data.get('in_place', instance.in_place)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

    def validate_phone(self, phone):
        return validate_phone_numbers(phone)


# noinspection PyMethodMayBeStatic
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
        fields = '__all__'


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = '__all__'
