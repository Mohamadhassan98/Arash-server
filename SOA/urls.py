from django.urls import path

from .views import *

urlpatterns = [
    path('signup/', Signup.as_view()),
    path('login/', Login.as_view()),
    path('add/arash/', AddArash.as_view()),
    path('add/license/', AddLicense.as_view()),
    path('add/company/', AddCompany.as_view()),
    path('add/request/', AddRequest.as_view()),
    path('user/<int:pk>/', Profile.as_view()),
    path('user/<int:pk>/logs/', GetLog.as_view()),
    path('company/<int:pk>/', CompanyOperations.as_view()),
    path('request/<int:pk>/', RequestOperations.as_view()),
    path('arash/<int:pk>/', ArashOperations.as_view()),
]
