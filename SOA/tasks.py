from SOA.models import Arash


# @background(schedule=1)
def check_arash_active(pk):
    arash = Arash.objects.get(pk=pk)
    arash.modify_active()
