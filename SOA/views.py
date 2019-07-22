from django.contrib.auth import login
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db import transaction
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *


# noinspection PyMethodMayBeStatic
class Signup(APIView):
    def is_master_admin(user):
        if user.status == 'ma':
            return True
        else:
            return False

    @method_decorator(login_required, name='dispatch')
    @method_decorator(user_passes_test(is_master_admin), name='dispatch')
    @transaction.atomic
    def post(self, request):
        try:
            with transaction.atomic():
                data = request.data
                print(data)
                address_serializer = AddressSerializer(data=data['address'])
                if address_serializer.is_valid():
                    address_serializer.save()
                else:
                    return Response(address_serializer.errors)

                data['address'] = address_serializer.data['id']

                user_serializer = UserSerializer(data=data)
                if user_serializer.is_valid():
                    user_serializer.save()
                else:
                    return Response(user_serializer.errors)

                return Response(user_serializer.data)

        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)


# noinspection PyMethodMayBeStatic
class Login(APIView):
    authentication_classes = []
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        user = User.objects.filter(username=username)
        if user.count() == 1:
            if user[0].check_password(password):
                login(request, user[0])
                return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def get(self, request):
        # when i write signup if the user is not master this url is required(it maybe need some change later)
        return Response("you are admin user can not access signup")

# noinspection PyMethodMayBeStatic
class AddArash(APIView):
    def post(self, request):
        serializer = ArashSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# noinspection PyMethodMayBeStatic
class ArashOperations(APIView):
    def delete(self, pk):
        try:
            Arash.objects.get(pk=pk).delete()
            return Response(status=status.HTTP_200_OK)
        except Arash.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get(self, pk):
        try:
            arash = Arash.objects.get(pk=pk)
            serializer = ArashSerializer(arash)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Arash.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            arash = Arash.objects.get(pk=pk)
            serializer = ArashSerializer(arash, request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Arash.DoesNotExist or serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)


# noinspection PyMethodMayBeStatic
class CompanyOperations(APIView):
    def get(self, pk):
        try:
            company = Company.objects.get(pk=pk)
            serializer = CompanySerializer(instance=company)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Company.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, pk):
        try:
            Company.objects.get(pk=pk).delete()
            return Response(status=status.HTTP_200_OK)
        except Company.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            company = Company.objects.get(pk=pk)
            serializer = CompanySerializer(company, request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Company.DoesNotExist or serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)


# noinspection PyMethodMayBeStatic
class AddRequest(APIView):
    def post(self, request):
        serializer = RequestSerializer(data=request.data)
        if serializer.is_valid():
            request = serializer.save()
            return Response(request, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# noinspection PyMethodMayBeStatic
class RequestOperations(APIView):
    def get(self, pk):
        try:
            request = Request.objects.get(pk=pk)
            serializer = RequestSerializer(instance=request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Request.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, pk):
        try:
            Request.objects.get(pk=pk).delete()
            return Response(status=status.HTTP_200_OK)
        except Request.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            request_object = Request.objects.get(pk=pk)
            serializer = RequestSerializer(request_object, request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Request.DoesNotExist or serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)


# noinspection PyMethodMayBeStatic
class AddLicense(APIView):
    def post(self, request):
        serializer = LicenseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddCompany(APIView):
    permission_classes = [IsAuthenticated, ]
    @transaction.atomic
    def post(self, request):
        try:
            with transaction.atomic():
                serializer = AddressSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                address = serializer.save()
                request.data._mutable = True
                request.data.update({'address': address.id})
                serializer = CompanySerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                # serializer.save(address=address)
                return Response(serializer.data)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)


# noinspection PyMethodMayBeStatic
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
