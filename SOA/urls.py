from django.urls import path

from .views import *

urlpatterns = [
    path('signup/', Signup.as_view()),
    path('accounts/login/', Login.as_view(), name='login'),
    path('add/arash/', AddArash.as_view()),
    path('add/company/', AddCompany.as_view()),
    path('companies/', GetCompanies.as_view()),
    path('add/request/', AddRequest.as_view()),
    path('user/<int:pk>/', Profile.as_view()),
    path('user/<int:pk>/logs/', GetLog.as_view()),
    path('company/<int:pk>/', CompanyOperations.as_view()),
    path('request/<int:pk>/', RequestOperations.as_view()),
    path('arash/<int:pk>/', ArashOperations.as_view()),
    path('company/<int:pk>/arashes/', GetArashes.as_view()),
    path('user-img/<int:pk>/', UserImage.as_view()),
    path('users/', GetUsers.as_view())
]
