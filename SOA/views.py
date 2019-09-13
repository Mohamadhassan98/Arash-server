from background_task.models import Task
from django.contrib.auth import login, logout
from django.db import transaction
from django.http import FileResponse
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *
from .tasks import *


# noinspection PyMethodMayBeStatic
class Signup(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            with transaction.atomic():
                data = request.data
                address_serializer = AddressSerializer(data=data['address'])
                address_serializer.is_valid(raise_exception=True)
                address_serializer.save()
                data['address'] = address_serializer.data['id']
                user_serializer = UserSerializer(data=data)
                user_serializer.is_valid(raise_exception=True)
                user = user_serializer.save()
                log = Log(user=request.user, operation='+', operand='User')
                log.add_or_remove_fields(user)
                log.save()
                return Response({'pk': user.id}, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# noinspection PyMethodMayBeStatic
class Login(APIView):
    authentication_classes = []
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                login(request, user)
                if not request.data['keep']:
                    request.session.set_expiry(0)
                serializer = UserLoginSerializer(instance=user)
                return Response(serializer.data)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist or KeyError:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


# noinspection PyMethodMayBeStatic
class GetProfile(APIView):
    def get(self, request):
        serializer = UserLoginSerializer(instance=request.user)
        return Response(serializer.data)


# noinspection PyMethodMayBeStatic
class LogOut(APIView):
    def get(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


# noinspection PyMethodMayBeStatic
class AddArash(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            with transaction.atomic():
                serializer = ArashSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                arash = serializer.save()
                log = Log(user=request.user, operation='+', operand='Arash')
                log.add_or_remove_fields(arash)
                log.save()
                check_arash_active(arash.pk, repeat=Task.DAILY, repeat_until=None)
                return Response(status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


# noinspection PyMethodMayBeStatic, PyUnusedLocal, DuplicatedCode
class ArashOperations(APIView):
    @transaction.atomic
    def delete(self, request, pk):
        try:
            with transaction.atomic():
                arash = Arash.objects.get(pk=pk)
                log = Log(operation='-', operand='Arash', user=request.user)
                log.add_or_remove_fields(arash)
                log.save()
                arash.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        except Arash.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk):
        try:
            arash = Arash.objects.get(pk=pk)
            serializer = ArashSerializer(arash)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Arash.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @transaction.atomic
    def put(self, request, pk):
        try:
            with transaction.atomic():
                arash = Arash.objects.get(pk=pk)
                old_arash = Arash.objects.get(pk=pk)
                serializer = ArashSerializer(arash, request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                new_arash = serializer.save()
                log = Log(operation='*', operand='Arash', user=request.user)
                log.edit_fields(old_arash, new_arash)
                log.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Arash.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class GetCompanies(ListAPIView):
    queryset = Company.objects.all()
    serializer_class = GetCompanySerializer


class GetArashes(ListAPIView):
    serializer_class = ArashSerializer
    queryset = Arash.objects.all()


# noinspection PyMethodMayBeStatic, PyUnusedLocal, DuplicatedCode
class CompanyOperations(APIView):
    def get(self, request, pk):
        try:
            company = Company.objects.get(pk=pk)
            serializer = GetCompanySerializer(instance=company)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Company.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @transaction.atomic
    def delete(self, request, pk):
        try:
            with transaction.atomic():
                company = Company.objects.get(pk=pk)
                log = Log(operation='-', operand='Company', user=request.user)
                log.add_or_remove_fields(company)
                log.save()
                company.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
        except Company.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @transaction.atomic
    def put(self, request, pk):
        try:
            with transaction.atomic():
                company = Company.objects.get(pk=pk)
                old_company = Company.objects.get(pk=pk)
                address = company.address
                address_serializer = AddressSerializer(address, request.data['address'])
                address_serializer.is_valid(raise_exception=True)
                address_serializer.save()
                request.data.pop('address')
                serializer = CompanySerializer(company, request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                new_company = serializer.save()
                log = Log(operation='*', operand='Company', user=request.user)
                log.edit_fields(old_company, new_company)
                log.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Company.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


# noinspection PyMethodMayBeStatic
class AddRequest(APIView):
    def post(self, request):
        # TODO Where is it after all?
        serializer = RequestSerializer(data=request.data)
        if serializer.is_valid():
            request = serializer.save()
            return Response(request, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# noinspection PyMethodMayBeStatic, PyUnusedLocal
class RequestOperations(APIView):
    # TODO Where is it after all?
    def get(self, request, pk):
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
class AddCompany(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            with transaction.atomic():
                serializer = AddressSerializer(data=request.data['address'])
                serializer.is_valid(raise_exception=True)
                address = serializer.save()
                request.data.update({'address': address.id})
                serializer = CompanySerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                company = serializer.save()
                log = Log(operation='+', operand='Company', user=request.user)
                log.add_or_remove_fields(company)
                log.save()
                return Response(status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class GetUsers(ListAPIView):
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()


# noinspection PyMethodMayBeStatic
class Profile(APIView):
    @transaction.atomic
    def put(self, request, pk):
        try:
            with transaction.atomic():
                user = User.objects.get(pk=pk)
                is_superuser = request.user.is_superuser
                if request.user.pk != pk and not is_superuser:
                    return Response(status=status.HTTP_403_FORBIDDEN)
                elif is_superuser:
                    old_user = User.objects.get(pk=pk)
                    data = request.data
                    if data['password'] == '':
                        data.pop('password')
                    address = user.address
                    address_serializer = AddressSerializer(address, data=data['address'])
                    address_serializer.is_valid(raise_exception=True)
                    address_serializer.save()
                    data.pop('address')
                    serializer = UserSerializer(user, data=data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    new_user = serializer.save()
                    log = Log(user=request.user, operation='*', operand='User')
                    log.edit_fields(old_user, new_user)
                    log.save()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                else:
                    data = {
                        'password': request.data['password']
                    }
                    serializer = UserSerializer(user, data=data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(status=status.HTTP_204_NO_CONTENT)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk):
        try:
            if request.user.id != pk and not request.user.is_superuser:
                return Response(status=status.HTTP_403_FORBIDDEN)
            user = User.objects.get(id=pk)
            serializer = UserProfileSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            is_superuser = request.user.is_superuser
            if request.user.pk == pk or not is_superuser:
                return Response(status=status.HTTP_403_FORBIDDEN)
            else:
                log = Log(user=request.user, operation='-', operand='User')
                log.add_or_remove_fields(user)
                log.save()
                user.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


# noinspection PyMethodMayBeStatic
class GetLog(APIView):
    def get(self, request, pk):
        try:
            if request.user.id != pk and not request.user.is_superuser:
                return Response(status=status.HTTP_403_FORBIDDEN)
            user = User.objects.get(pk=pk)
            logs = Log.objects.filter(user=user)
            serializer = LogSerializer(logs, many=True)
            if not serializer.data:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


# noinspection PyMethodMayBeStatic
class UserImage(APIView):
    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            if request.user.pk != pk and not request.user.is_superuser:
                return Response(status=status.HTTP_403_FORBIDDEN)
            return FileResponse(user.profile_pic)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            if request.user.pk != pk and not request.user.is_superuser:
                return Response(status=status.HTTP_403_FORBIDDEN)
            if user.profile_pic.name != 'default.png':
                user.profile_pic.delete()
            user.profile_pic = request.data["profile_pic"]
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            if request.user.pk != pk and not request.user.is_superuser:
                return Response(status=status.HTTP_403_FORBIDDEN)
            if user.profile_pic.name != 'default.png':
                user.profile_pic.delete()
                user.profile_pic = None
                user.save()
                # Todo Test
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
