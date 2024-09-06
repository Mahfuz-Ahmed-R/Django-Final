from . import views
from django.urls import path

urlpatterns = [
    path('initiate-payment/', views.initiate_payment, name='initiate_payment'),
]