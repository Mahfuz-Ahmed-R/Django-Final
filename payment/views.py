from django.shortcuts import redirect
from sslcommerz_lib import SSLCOMMERZ
from api.models import Order, Customer
import random, string
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response

def generate_transaction_id(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

transaction_id = generate_transaction_id()

@csrf_exempt
@api_view(['POST'])
def initiate_payment(request, amount, order_id, user_id):
    from api.serializers import SSLCommerzResponseSerializer  # Moved import here

    user = User.objects.get(id=user_id)
    order = Order.objects.get(id=order_id)
    customer = Customer.objects.get(user=user)
    settings = {
        'store_id': 'forev66dab988a89cf',
        'store_pass': 'forev66dab988a89cf@ssl',
        'issandbox': True
    }
    sslcz = SSLCOMMERZ(settings)
    post_body = {
        'total_amount': amount + 60,
        'currency': 'BDT',
        'tran_id': transaction_id,
        'success_url': 'https://django-final-n0lr.onrender.com/myorders/',
        'fail_url': 'https://django-final-n0lr.onrender.com/order-item/',
        'cancel_url': 'https://django-final-n0lr.onrender.com/order-item/',
        'cus_name': user.username,
        'cus_email': user.email,
    }

    # Initiating the SSLCOMMERZ session
    response_data = sslcz.createSession(post_body)
    
    # Serialize the response data
    serializer = SSLCommerzResponseSerializer(data=response_data)
    if serializer.is_valid():
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=400)