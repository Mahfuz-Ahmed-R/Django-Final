from django.urls import path
from .views import InitiatePayment, PaymentSuccess, PaymentFail, PaymentCancel

urlpatterns = [
    path('initiate/<int:order_id>/<int:user_id>/', InitiatePayment.as_view(), name='payment-initiate'),
    path('success/', PaymentSuccess.as_view(), name='payment-success'),
    path('fail/', PaymentFail.as_view(), name='payment-fail'),
    path('cancel/', PaymentCancel.as_view(), name='payment-cancel'),
]
