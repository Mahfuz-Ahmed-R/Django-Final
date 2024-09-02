from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from . import models
from . import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .constants import users_idd
from rest_framework import generics

class InvetoryGetView(generics.ListAPIView):
    serializer_class = serializers.InventorySerializer

    def get_queryset(self):
        product_id = self.kwargs.get('id')
        queryset = models.InventoryModel.objects.filter(product=product_id)
        return queryset
    
class ProductViewSet(viewsets.ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer

class ProductByCategoryView(generics.ListAPIView):
    serializer_class = serializers.ProductSerializer

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        subcategory_slug = self.kwargs.get('subcategory_slug')
        
        queryset = models.Product.objects.all()
        
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        if subcategory_slug:
            queryset = queryset.filter(subcategory__slug=subcategory_slug)
        
        return queryset
    
class ProductByCategoryViewByPrice(generics.ListAPIView):
    serializer_class = serializers.ProductSerializer

    def get_queryset(self):
        pk = self.kwargs.get('id', None)

        if pk == 1:
            queryset = models.Product.objects.all().order_by('price')
        elif pk == 2:
            queryset = models.Product.objects.all().order_by('-price')
        else:
            queryset = models.Product.objects.all()
        return queryset


class OrderViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer

class OrderItemViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = models.OrderItem.objects.all()
    serializer_class = serializers.OrderItemSerializer

class MyOrdersViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = models.MyOrdersModel.objects.all()
    serializer_class = serializers.MyOrderSerializer

class OrderItemDeleteView(APIView):
    def delete(self, request, pk, id, format=None):
        serializer = serializers.OrderItemSerializer()
        try:
            order_item = serializer.delete_order_item(pk, id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except serializers.ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class MyOrderDeleteView(APIView):
    def delete(self, request, pk, format=None):
        serializer = serializers.CancelOrder()
        try:
            myorders_item = serializer.delete_order_item(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except serializers.ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class WishListViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = models.WishListModel.objects.all()
    serializer_class = serializers.WishListSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = models.ReviewModel.objects.all()
    serializer_class = serializers.ReviewSerializer

class ShippingAddressViewSet(viewsets.ModelViewSet):
    queryset = models.ShippingAddress.objects.all()
    serializer_class = serializers.ShippingSerializer

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = models.InventoryModel.objects.all()
    serializer_class = serializers.InventorySerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = models.Customer.objects.all()
    serializer_class = serializers.CustomerSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer

class SubCategoryViewSet(viewsets.ModelViewSet):
    queryset = models.SubCategory.objects.all()
    serializer_class = serializers.SubCategorySerializer

class SizeViewSet(viewsets.ModelViewSet):
    queryset = models.Size.objects.all()
    serializer_class = serializers.SizeSerializer

class ColorViewSet(viewsets.ModelViewSet):
    queryset = models.Color.objects.all()
    serializer_class = serializers.ColorSerializer

class CustomerDetail(APIView):
    def get(self, request, user_id):
        customer = get_object_or_404(models.Customer, user__id=user_id)
        serializer = serializers.CustomerSerializer(customer)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class OrderDetail(APIView):
    def get(self, request, user_id):
        customer = get_object_or_404(models.Customer, user__id=user_id)
        order = get_object_or_404(models.Order, customer=customer)
        serializer = serializers.OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UserRegistrationAPIView(APIView):
    def post(self, request):
        serializer = serializers.RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            confirm_link = f"https://django-final-n0lr.onrender.com/active/{uid}/{token}"
            email_subject = "Confirm Email"
            email_body = render_to_string('confirm_email.html', {'confirm_link': confirm_link})
            email = EmailMultiAlternatives(email_subject, email_body, to=[user.email])
            email.attach_alternative(email_body, "text/html")
            email.send()
            return Response("Check your mail for confirmation", status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def activate(request, uid64, token):
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = models.User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, models.User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        customer = models.Customer.objects.create(user=user, name=user.first_name, email=user.email)
        customer.save()
        return redirect('https://foreverstoree.netlify.app/login')
    else:
        return Response("Invalid Activation Link")

class UserLoginView(APIView):
    def post(self, request):
        serializer = serializers.UserLoginSerializer(data=self.request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
                
            if user:
                login(request, user)
                users_idd = user.id
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'token':str(token), 'user_id':user.id})
            else:
                return Response("Invalid Credentials")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserLogoutView(APIView):
    def get(self, request):
        request.user.auth_token.delete()
        logout(request)
        return redirect('register')
