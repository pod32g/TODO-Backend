from django.urls import path
from mainapp import views

urlpatterns = [
    path('', views.MainApp.as_view(), name="Todo")
]
