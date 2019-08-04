from django.contrib import admin

from SOA.models import *
from SOAConnection.models import *

admin.site.register(User)
admin.site.register(Arash)
admin.site.register(Address)
admin.site.register(Company)
admin.site.register(Log)
admin.site.register(Information)
