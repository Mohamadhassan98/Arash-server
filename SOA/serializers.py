from rest_framework import serializers

from .models import Address, User, License, Arash, Company


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('is_superuser', 'is_staff', 'date_joined', 'last_login', 'groups', 'user_permissions', 'is_active')
        depth = 1

    def create(self, validated_data) -> User:
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        return User.objects.create_user(username=username, password=password, **validated_data)


class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = License
        fields = '__all__'


class ArashSerializer(serializers.ModelSerializer):
    class Meta:
        model = Arash
        fields = '__all__'


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'
