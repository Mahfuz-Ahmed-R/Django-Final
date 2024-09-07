from django.shortcuts import redirect
from sslcommerz_lib import SSLCOMMERZ
from api.models import Order, Customer
import random, string
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api import models, serializers
from rest_framework.exceptions import NotFound
from rest_framework import status

def generate_transaction_id(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

transaction_id = generate_transaction_id()

@csrf_exempt
@api_view(['POST'])
def initiate_payment(request):
    data = request.data
    amount = data['amount']
    order = data['order']
    user = data['user']
    settings = {
        'store_id': 'forev66dab988a89cf',
        'store_pass': 'forev66dab988a89cf@ssl',
        'issandbox': True
    }
    sslcz = SSLCOMMERZ(settings)
    post_body = {
        'total_amount': amount,
        'currency': 'BDT',
        'tran_id': transaction_id,
        'success_url': 'https://django-final-n0lr.onrender.com/myorders/',
        'fail_url': 'https://django-final-n0lr.onrender.com/order-item/',
        'cancel_url': 'https://django-final-n0lr.onrender.com/order-item/',
        'cus_name': User.objects.get(id=user).username,
        'cus_email': User.objects.get(id=user).email,
    }

    # Create SSLCOMMERZ session
    response_data = sslcz.createSession(post_body)
    
    return Response({'payment_url': response_data.get('GatewayPageURL')})

# @csrf_exempt
# @api_view(['GET'])
# def payment_success(request, order_id):
#     order = Order.objects.get(id=order_id)
#     order.is_paid = True
#     order.save()
#     try:
#         order = models.Order.objects.get(id=order_id)
#         user = order.user
#     except models.Order.DoesNotExist:
#         return Response({'error': 'Order not found'}, status=404)
    
#     # Prepare shipping address data (this could be from session or database)
#     shipping_data = {
#         'order': order.id,
#         'user': user.id,
#         'street': 'Address',  # Use actual address
#         'city': 'City',
#         'state': 'State',
#         'zipcode': 'Zipcode',
#         'country': 'Country',
#         'payment': 'sslcommerz',
#         'amount': order.total_amount,  
#     }
    
#     serializer = serializers.ShippingSerializer(data=shipping_data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response({'message': 'Shipping address created successfully'})
#     return Response(serializer.errors, status=400)
    