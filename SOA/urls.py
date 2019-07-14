from django.urls import path

from .views import Signup, GetUser

urlpatterns = [
    path('signup/', Signup.as_view()),
    path('user/<int:id>/', GetUser.as_view())

]
