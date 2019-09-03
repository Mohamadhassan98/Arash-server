import random
import secrets
import string
from datetime import datetime

import cryptography
from OpenSSL import crypto
# from background_task.models import Task
from cryptography.hazmat.backends import default_backend
from django.core.files import File
from django.db import transaction
from django.http import FileResponse
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Information, Token, ArashVersion
from .serializers import InformationSerializer, TokenSerializer
from .tasks import *


class GetRandom(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        # create random key size=45 with digits and string
        size = 45
        chars = string.ascii_uppercase + string.digits
        rand = ''.join(random.choice(chars) for _ in range(size))
        # get ip from request
        try:
            ip = request.META['HTTP_X_FORWARDED_FOR']
        except:
            ip = request.META['REMOTE_ADDR']
        # check ip is new or not
        try:
            last_req = Information.objects.get(ip=ip)
            if last_req.date_request == datetime.now().strftime("%d-%m-%y"):
                if last_req.counter >= 3:
                    text = "should be blocked"  # TODO: how block it
                    return Response(text, status=status.HTTP_400_BAD_REQUEST)  # todo
                else:
                    last_req.counter += 1
                    last_req.time_request = datetime.now().strftime("%H:%M:%S")
                    last_req.random = rand
                    last_req.save()
                    return Response(rand, status=status.HTTP_200_OK)
            else:
                last_req.counter = 1
                last_req.time_request = datetime.now().strftime("%H:%M:%S")
                last_req.date_request = datetime.now().strftime("%d-%m-%y")
                last_req.random = rand
                last_req.save()
                return Response(rand, status=status.HTTP_200_OK)

        except Information.DoesNotExist:
            data = {
                'ip': ip, 'public_key': request.data['public_key'],
                'random': rand,
                'date_request': datetime.now().strftime("%d-%m-%y"),
                'time_request': datetime.now().strftime("%H:%M:%S")
            }
            information_serializer = InformationSerializer(data=data)
            if information_serializer.is_valid():
                information_serializer.save()
                return Response(rand, status=status.HTTP_200_OK)
            return Response("data is invalid", status=status.HTTP_400_BAD_REQUEST)


class VerifySignature(APIView):
    permission_classes = []
    authentication_classes = []

    @staticmethod
    def verify_signature(signature: bytes, raw_message: bytes, public_key: bytes) -> bool:
        p = cryptography.hazmat.primitives.serialization.load_pem_public_key(public_key, default_backend())
        p = crypto.PKey().from_cryptography_key(p)
        cert = crypto.X509()
        cert.set_pubkey(p)
        try:
            crypto.verify(cert, signature, raw_message, digest='SHA256')
            return True
        except:
            return False

    def post(self, request):
        try:
            public_key = request.data['public_key'].encode('utf-8').decode('unicode_escape')
            signature = request.data['signature'].encode('latin_1').decode('unicode_escape')
            print(signature.encode('latin_1'))
            print(public_key.encode())
            last_req = Information.objects.get(public_key=public_key)
            raw_message = str(last_req.random)
            print(raw_message.encode())
            if self.verify_signature(signature=signature.encode('latin_1'),
                                     raw_message=raw_message.encode(),
                                     public_key=public_key.encode()):
                token = secrets.token_hex()
                check_req = Token.objects.filter(public_key=last_req.public_key)
                if check_req.count() == 0:
                    data = {'public_key': last_req.public_key, 'token': token,
                            'date_request': datetime.now().strftime("%d-%m-%y"),
                            'time_request': datetime.now().strftime("%H:%M:%S")}
                    token_serializer = TokenSerializer(data=data)
                    token_serializer.is_valid(raise_exception=True)
                    token_serializer.save()
                    return Response(token, status=status.HTTP_200_OK)
                else:
                    if check_req.date_request == datetime.now().strftime("%d-%m-%y"):
                        if check_req.counter >= 3:
                            text = "should be blocked"
                            return Response(text, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            check_req.counter += 1
                            check_req.time_request = datetime.now().strftime("%H:%M:%S")
                            check_req.token = token
                            check_req.save()
                            return Response(token, status=status.HTTP_200_OK)
                    else:
                        check_req.counter = 1
                        check_req.time_request = datetime.now().strftime("%H:%M:%S")
                        check_req.date_request = datetime.now().strftime("%d-%m-%y")
                        check_req.token = token
                        check_req.save()
                        return Response(token, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        except Information.DoesNotExist:
            return Response("Arash does not exist", status=status.HTTP_404_NOT_FOUND)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)


class Update(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        # try:
        token = Token.objects.get(token=request.data['token'])
        public_key = token.public_key
        arash_version = Arash.objects.get(public_key=public_key).version
        last_version = ArashVersion.objects.order_by('-time')[0].version
        if arash_version == last_version:
            return Response("You Have Latest Version", status=status.HTTP_200_OK)
        else:

            file = File(open(ArashVersion.objects.order_by('-time')[0].file, 'rb'))
            return FileResponse(file)
            #  return Response("New Version is available", status=status.HTTP_200_OK)

    # except Exception as e :
    #     print(e)
    #     return Response("Token Does Not2 Exist", status=status.HTTP_400_BAD_REQUEST)


class UpdateConfirm(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        token = Token.objects.get(token=request.data['token'])
        public_key = token.public_key
        arash_version = ArashVersion.objects.order_by('-time')[0].version
        arash = Arash.objects.filter(public_key=public_key).update(version=arash_version)
        return Response("Version Updated", status=status.HTTP_200_OK)


class LiveRequest(APIView):
    permission_classes = []
    authentication_classes = []

    @transaction.atomic
    def get(self, request):
        try:
            with transaction.atomic():
                token = Token.objects.get(token=request.data['token'])
                public_key = token.public_key
                arash = Arash.objects.get(public_key=public_key)
                arash.status = 'alv'
                arash.save()
                AliveRequest.objects.update_or_create(public_key=public_key)
                check_arash_status(pk=arash.pk, repeat=300, repeat_until=None)
                return Response(status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
