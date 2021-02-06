from django.urls import path
from authentication import views

urlpatterns = [
    path('login', views.Login.as_view(), name='Login'),
    path('logout', views.Logout.as_view(), name='Logout')
]
