from django.contrib.auth import login
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *


class Signup(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Login(APIView):
    authentication_classes = []
    permission_classes = (AllowAny,)

    def post(self, request):
        print('start')
        username = request.data['username']
        password = request.data['password']
        user = User.objects.filter(username=username)
        print(user[0])
        if user.count() == 1:
            if user[0].check_password(password):
                login(request, user[0])
                return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class AddArash(APIView):
    def post(self, request):
        serializer = ArashSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddLicense(APIView):
    def post(self, request):
        serializer = LicenseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddCompany(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            serializer = AddressSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            address = serializer.save()

            serializer = CompanySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(address=address)
            return Response(serializer.data)
        except serializers.ValidationError as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)


# noinspection PyMethodMayBeStatic
class AddRequest(APIView):
    def post(self, request):
        serializer = RequestSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class Profile(APIView):
    def put(self, request, pk):
        try:
            user = User.objects.get(pk)
            if request.user.pk != pk:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                data = request.data
                serializer = UserSerializer(user, data=data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist or serializers.ValidationError as e:
            return Response(e.details, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk):
        try:
            user = User.objects.get(id=pk)
            serializer = UserSerializer(user)
            login(user=user, request=request)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
