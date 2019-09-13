from background_task import background

from SOA.models import Arash
from SOAConnection.models import AliveRequest


@background(schedule=1)
def check_arash_status(pk):
    try:
        arash = Arash.objects.get(pk=pk)
        last_request = AliveRequest.objects.get(public_key=arash.public_key).date_time
        arash.modify_status(last_request)
    except AliveRequest.DoesNotExist:
        AliveRequest.objects.create(public_key=arash.public_key)
