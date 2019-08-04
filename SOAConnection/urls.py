from django.urls import path

from .views import *

urlpatterns = [
    path('getrandom/', GetRandom.as_view()),
]
