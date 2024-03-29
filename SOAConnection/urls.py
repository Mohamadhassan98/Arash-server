from django.urls import path

from .views import *

urlpatterns = [
    path('getrandom/', GetRandom.as_view()),
    path('verify/', VerifySignature.as_view()),
    path('update/', Update.as_view()),
    path('liverequest/', LiveRequest.as_view()),
]
