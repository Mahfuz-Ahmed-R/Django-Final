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
from api import serializers, models
from django.core.mail import send_mail

def generate_transaction_id(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

transaction_id = generate_transaction_id()

class InitiatePayment(APIView):
    def post(self, request, order_id, user_id, *args, **kwargs):
        user = User.objects.get(id=user_id)
        order = Order.objects.get(id=order_id)
        settings = { 'store_id': 'forev66dab988a89cf', 'store_pass': 'forev66dab988a89cf@ssl', 'issandbox': True }
        sslcz = SSLCOMMERZ(settings)
        post_body = {}
        post_body['total_amount'] = order.get_cart_total + 60
        post_body['currency'] = "BDT"
        post_body['tran_id'] = transaction_id
        post_body['success_url'] = f'https://django-final-n0lr.onrender.com/payment/success/{order_id}/{user_id}/'
        post_body['fail_url'] = f'https://django-final-n0lr.onrender.com/payment/fail/{order_id}/{user_id}/'
        post_body['cancel_url'] = f'https://django-final-n0lr.onrender.com/payment/cancel/{order_id}/{user_id}/'
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
        return Response({'payment_url': response['GatewayPageURL']}, status=status.HTTP_200_OK)

class PaymentSuccess(APIView):
    def post(self, request, order_id, user_id, *args, **kwargs):
        try:
            # Fetch the order and customer data
            order_instance = models.Order.objects.get(id=order_id)
            customer = models.Customer.objects.get(user=user_id)
        except models.Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

        # Calculate the total amount
        amount = order_instance.get_cart_total + 60

        # Prepare the data for the ShippingSerializer
        shipping_data = {
            'user': user_id,
            'customer': customer.id, 
            'order': order_instance.id,
            'street':'street',
            'city':'city',
            'state':'state',
            'zipcode':'zipcode',
            'country':'country',
            'payment': 'sslcommerz',
            'amount': amount
        }

        # Initialize the serializer with data
        serializer = serializers.ShippingSerializer(data=shipping_data)

        # Validate and save the shipping address
        if serializer.is_valid():
            serializer.save()  # Save the shipping address

            # Handle order items and create MyOrdersModel entries
            order_items = models.OrderItem.objects.filter(order=order_id)
            for item in order_items:
                product = item.product
                size = item.size
                quantity = item.quantity

                models.MyOrdersModel.objects.get_or_create(
                    customer=customer,
                    product=product,
                    order=order_instance,
                    size=size,
                    quantity=quantity
                )

            # Update order status and clean up order items
            order_instance.status = "Successful"
            order_instance.save()

            # Optionally, delete order items after processing
            models.OrderItem.objects.filter(order=order_id).delete()

            return Response({'message': 'Payment successful and shipping address created'}, status=status.HTTP_200_OK)
        
        # Return validation errors from the serializer
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        

class PaymentCancel(APIView):
    def post(self, request, order_id, user_id, *args, **kwargs):
        # Extract order ID from request or session
        user = User.objects.get(id=user_id) 

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
    def post(self, request, order_id, user_id, *args, **kwargs):
        # Extract order ID from request or session
        user = User.objects.get(id=user_id)
        
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