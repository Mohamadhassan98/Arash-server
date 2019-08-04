import random
import string
from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Information
from .serializers import InformationSerializer


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
            data = {'ip': ip, 'public_key': request.data['public_key'], 'random': rand,
                    'date_request': datetime.now().strftime("%d-%m-%y"),
                    'time_request': datetime.now().strftime("%H:%M:%S")}
            information_serializer = InformationSerializer(data=data)
            if information_serializer.is_valid():
                information_serializer.save()
                return Response(rand, status=status.HTTP_200_OK)
            return Response("data is invalid", status=status.HTTP_400_BAD_REQUEST)
