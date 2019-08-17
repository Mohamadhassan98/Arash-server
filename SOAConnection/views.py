import random
import secrets
import string
from datetime import datetime

import cryptography
from OpenSSL import crypto
from cryptography.hazmat.backends import default_backend
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Information, Token
from .serializers import InformationSerializer, TokenSerializer


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
            last_req = Information.objects.filter(ip=ip)[0]
            print(last_req)
            if last_req.date_request == datetime.now().strftime("%d-%m-%y"):
                if last_req.counter > 3:
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

        except:
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

    @staticmethod
    def verify_signature(signature: bytes, raw_message: bytes, public_key: str) -> bool:
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
            last_req = Information.objects.filter(public_key=request.data['public_key'])[0]
            raw_message = last_req.random
            if self.verify_signature(request.data['signature'], raw_message, last_req.public_key):
                token = secrets.token_hex()
                check_req = Token.objects.filter(public_key=last_req.public_key)
                if check_req.count() == 0:
                    data = {'public_key': last_req.public_key, 'token': token,
                            'date_request': datetime.now().strftime("%d-%m-%y"),
                            'time_request': datetime.now().strftime("%H:%M:%S")}
                    token_serializer = TokenSerializer(data=data)
                    if token_serializer.is_valid():
                        token_serializer.save()
                        return Response(token, status=status.HTTP_200_OK)
                    return Response(status=status.HTTP_400_BAD_REQUEST)

                else:
                    if check_req.date_request == datetime.now().strftime("%d-%m-%y"):
                        if check_req.counter > 3:
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
        except:
            return Response("Arash does not exist", status=status.HTTP_400_BAD_REQUEST)
