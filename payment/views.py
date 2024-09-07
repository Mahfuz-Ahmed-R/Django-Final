from django.shortcuts import redirect
from sslcommerz_lib import SSLCOMMERZ
from api.models import Order, Customer, ShippingAddress, OrderItem, MyOrdersModel
import random, string
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.conf import settings
from api import serializers
from django.core.mail import send_mail

def generate_transaction_id(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

transaction_id = generate_transaction_id()

class InitiatePayment(APIView):
    def post(self, request, order_id, user_id, *args, **kwargs):
        data=request.data
        user = User.objects.get(id=user_id)
        order = Order.objects.get(id=order_id)
        settings = { 'store_id': 'forev66dab988a89cf', 'store_pass': 'forev66dab988a89cf@ssl', 'issandbox': True }
        sslcz = SSLCOMMERZ(settings)
        post_body = {}
        post_body['total_amount'] = order.get_cart_total + 60
        post_body['currency'] = "BDT"
        post_body['tran_id'] = transaction_id
        post_body['success_url'] = 'https://django-final-n0lr.onrender.com/payment/success/'
        post_body['fail_url'] = 'https://django-final-n0lr.onrender.com/payment/fail/'
        post_body['cancel_url'] = 'https://django-final-n0lr.onrender.com/payment/cancel/'
        post_body['emi_option'] = 0
        post_body['cus_name'] = user.username
        post_body['cus_email'] = user.email
        post_body['cus_phone'] = "01700000000"
        post_body['cus_add1'] = "customer address"
        post_body['cus_city'] = "Dhaka"
        post_body['cus_country'] = "Bangladesh"
        post_body['shipping_method'] = "NO"
        post_body['multi_card_name'] = ""
        post_body['num_of_item'] = order.get_cart_items
        post_body['product_name'] = "Test"
        post_body['product_category'] = "Test Category"
        post_body['product_profile'] = "general"

        response = sslcz.createSession(post_body)
        print("SSLCOMMERZ Response:", response)
        return Response({'payment_url': response['GatewayPageURL']}, status=status.HTTP_200_OK)

class PaymentSuccess(APIView):
    def post(self, request, *args, **kwargs):
        # # Handle the success callback from SSLCOMMERZ
        data = request.data
        # transaction_id = data.get('tran_id')
        # payment_status = data.get('status')
        print(f"Received callback data: {data}")
        
        # # Verify the payment status with SSLCOMMERZ (implement this verification)
        # if payment_status == 'Successful':  # Check the actual status returned
        #     # Retrieve payment details and process shipping
        #     data = {
        #         'order': data.get('order_id'),
        #         'user': data.get('user_id'),
        #         'name': data.get('cus_name'),
        #         'email': data.get('cus_email'),
        #         'street': data.get('cus_add1'),
        #         'city': data.get('cus_city'),
        #         'state': data.get('state'),
        #         'zipcode': data.get('zipcode'),
        #         'country': data.get('cus_country'),
        #         'payment': 'sslcommerz',
        #         'amount': data.get('total_amount')
        #     }
        #     serializer = serializers.ShippingSerializer(data=data)
        #     if serializer.is_valid():
        #         serializer.save()
        #         return Response({'message': 'Payment successful and shipping address created'}, status=status.HTTP_200_OK)
        #     return Response({'message': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'message': 'Payment done'}, status=status.HTTP_200_OK)
        # return Response({'message': 'Payment failed or canceled'}, status=status.HTTP_400_BAD_REQUEST)


class PaymentCancel(APIView):
    def post(self, request, *args, **kwargs):
        # Extract order ID from request or session
        order_id = request.query_params.get('order_id')
        user = request.query_params.get('user_id')
        main_user = User.objects.get(id=user)
        
        if not order_id:
            return Response({'error': 'Order ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Update order status to 'Cancelled'
            order = Order.objects.get(id=order_id)
            order.status = 'Cancelled'
            order.save()

            # Send cancellation email to user
            send_mail(
                'Payment Cancelled',
                'Your payment has been cancelled. If this was a mistake, please try again.',
                'from@example.com',
                [user.email],
                fail_silently=False,
            )

            return Response({'message': 'Payment cancelled and order status updated'}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

class PaymentFail(APIView):
    def post(self, request, *args, **kwargs):
        # Extract order ID from request or session
        order_id = request.query_params.get('order_id')
        user = request.query_params.get('user_id')
        main_user = User.objects.get(id=user)
        
        if not order_id:
            return Response({'error': 'Order ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Update order status to 'Cancelled'
            order = Order.objects.get(id=order_id)
            order.status = 'Failed'
            order.save()

            # Send cancellation email to user
            send_mail(
                'Payment Failed',
                'Your payment has been Failed. If this was a mistake, please try again.',
                'from@example.com',
                [user.email],
                fail_silently=False,
            )
        except:
            return Response({'message': 'Payment failed'}, status=status.HTTP_400_BAD_REQUEST)