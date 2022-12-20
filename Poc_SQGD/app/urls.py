from django.urls import path
from . import views

urlpatterns = [
    path('aws_iot_bulk_register_things', views.aws_iot_bulk_register_things),
]