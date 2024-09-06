from . import views
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('initiate-payment', views.initiate_payment)

urlpatterns = [
    path('', include(router.urls)),
]