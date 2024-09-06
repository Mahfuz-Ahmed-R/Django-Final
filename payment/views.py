from django.shortcuts import redirect
from sslcommerz_lib import SSLCOMMERZ
from api.models import Order, Customer
import random,string
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from api.serializers import SSLCommerzResponseSerializer
from rest_framework.response import Response

def generate_transaction_id(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

transaction_id = generate_transaction_id()

# @csrf_exempt
# def payment(request, user_id, amount, street):
#     user = User.objects.get(id=user_id)
#     customer = Customer.objects.get(customer=user)
#     order_qs = Order.objects.filter(customer=customer, ordered=False)
#     total_price = order_qs.get_cart_total
#     total_cart = order_qs.get_cart_items
    
#     settings = { 'store_id': 'forev66dab988a89cf', 'store_pass': 'forev66dab988a89cf@ssl', 'issandbox': True }
#     sslcz = SSLCOMMERZ(settings)
#     post_body = {}
#     post_body['total_amount'] = amount + 60
#     post_body['currency'] = "BDT"
#     post_body['tran_id'] = transaction_id
#     post_body['success_url'] = "https://django-final-n0lr.onrender.com/myorders/"
#     post_body['fail_url'] = "https://django-final-n0lr.onrender.com/order-item/"
#     post_body['cancel_url'] = "https://django-final-n0lr.onrender.com/order-item/"
#     post_body['emi_option'] = 0
#     post_body['cus_name'] = user.username
#     post_body['cus_email'] = user.email
#     post_body['cus_phone'] = "01700000000"
#     post_body['cus_add1'] = street
#     post_body['cus_city'] = "Dhaka"
#     post_body['cus_country'] = "Bangladesh"
#     post_body['shipping_method'] = "YES"
#     post_body['multi_card_name'] = ""
#     post_body['num_of_item'] = total_cart
#     post_body['product_name'] = "Test"
#     post_body['product_category'] = "Test Category"
#     post_body['product_profile'] = "general"

#     response = sslcz.createSession(post_body)
#     if response['status'] == 'SUCCESS':
#         return {'status': 'SUCCESS', 'GatewayPageURL': response['GatewayPageURL']}
#     else:
#         return {'status': 'FAILED', 'message': response['failedreason']}

@csrf_exempt
@api_view(['POST'])
def initiate_payment(request):
    if request.method == 'POST':
        data = request.data 
        amount = data['amount']
        street = data['street']
        user_id = data['user']

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
            'cus_name': request.user.username,
            'cus_email': request.user.email,
            'cus_add1': street,
            'cus_city': data['city'],
            'cus_country': data['country'],
        }

        # Initiating the SSLCOMMERZ session
        response_data = sslcz.createSession(post_body)
        
        # Serialize the response data
        serializer = SSLCommerzResponseSerializer(data=response_data)
        if serializer.is_valid():
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)

