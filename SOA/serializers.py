import re

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import *


def validate_phone_numbers(phone):
    regex = r'^0\d{10}'
    if not re.search(regex, phone):
        raise ValidationError('phone must be an 11 digit number')
    return phone


def validate_mobile_numbers(phone):
    regex = r'^09\d{9}'
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
        if fax == '':
            return fax
        return validate_phone_numbers(fax)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'id', 'first_name', 'last_name', 'email', 'phone', 'personnel_code', 'is_superuser',
                  'address', 'in_place']
        depth = 1


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'is_superuser']


# noinspection PyMethodMayBeStatic
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('is_staff', 'date_joined', 'last_login', 'groups', 'user_permissions', 'is_active', 'profile_pic')

    def create(self, validated_data) -> User:
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        return User.objects.create_user(username=username, password=password, **validated_data)

    def update(self, instance: User, validated_data) -> User:
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.is_superuser = validated_data.get('is_superuser', instance.is_superuser)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.personnel_code = validated_data.get('personnel_code', instance.personnel_code)
        instance.in_place = validated_data.get('in_place', instance.in_place)
        instance.save()
        return instance

    def validate_phone(self, phone):
        return validate_mobile_numbers(phone)


class ArashSerializer(serializers.ModelSerializer):
    class Meta:
        model = Arash
        fields = '__all__'


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        exclude = ('company_code',)

    def create(self, validated_data):
        from datetime import datetime
        str1 = datetime.now()
        str2 = str1.strftime("%m/%d/%Y")
        str3 = validated_data['name']
        company = Company.objects.filter(name=str3)
        if company.count() != 0:
            str4 = company.count() + 1
            return Company.objects.create(company_code=str2 + str3 + str(str4), **validated_data)
        else:
            return Company.objects.create(company_code=str2 + str3 + '0', **validated_data)


class GetCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'
        depth = 1


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = '__all__'


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = '__all__'
