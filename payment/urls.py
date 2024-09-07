from django.urls import path
from .views import InitiatePayment, PaymentSuccess, PaymentFail, PaymentCancel

urlpatterns = [
    path('initiate/<int:order_id>/<int:user_id>/', InitiatePayment.as_view(), name='payment-initiate'),
    path('success/<int:order>/<int:user_id>/', PaymentSuccess.as_view(), name='payment-success'),
    path('fail/<int:order>/<int:user_id>/', PaymentFail.as_view(), name='payment-fail'),
    path('cancel/<int:order>/<int:user_id>/', PaymentCancel.as_view(), name='payment-cancel'),
]
