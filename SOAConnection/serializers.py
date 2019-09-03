from rest_framework import serializers

from .models import Information, Token, AliveRequest


class InformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Information
        fields = '__all__'


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = '__all__'


class AliveRequestSerializer(serializers.ModelSerializer):
    class meta:
        model = AliveRequest
        fields = '__all__'
