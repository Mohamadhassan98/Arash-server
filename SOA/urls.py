from django.urls import path

from .views import *

urlpatterns = [
    path('signup/', Signup.as_view()),
    path('login/', Login.as_view()),
    path('user/<int:id>/', GetUser.as_view()),
    path('add/arash/', AddArash.as_view()),
    path('add/license/', AddLicense.as_view()),


]
