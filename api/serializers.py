from django.forms import ValidationError
from rest_framework import serializers
from . import models
from django.contrib.auth.models import User
from rest_framework.exceptions import NotFound


from .constants import users_idd


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Color
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Customer
        fields = '__all__'

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Size
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = '__all__'

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SubCategory
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    size = serializers.StringRelatedField(many=False)
    color = serializers.StringRelatedField(many=False)
    category = serializers.StringRelatedField(many=False)
    subcategory = serializers.StringRelatedField(many=False)
    rating = serializers.SerializerMethodField()
    class Meta:
        model = models.Product
        fields =[
            'id',
            'name',
            'description',
            'price',
            'image_1',
            'image_2',
            'image_3',
            'size',
            'color',
            'category',
            'subcategory',
            'rating',
        ]

    def get_rating(self, obj):
        return obj.get_rating

class InventorySerializer(serializers.ModelSerializer):
    size = serializers.StringRelatedField(many=False)
    # product = serializers.StringRelatedField(many=False)
    class Meta:
        model = models.InventoryModel
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField(many=False)
    cart_total = serializers.SerializerMethodField()
    cart_item = serializers.SerializerMethodField()
    transaction_id = serializers.SerializerMethodField()
    class Meta:
        model = models.Order
        fields = [
            'id',
            'customer',
            'date_ordered',
            'complete',
            'cart_total',
            'cart_item',
            'transaction_id',
        ]

    def get_transaction_id(self, obj):
        return obj.get_transaction_id
    
    def get_cart_total(self, obj):
        return obj.get_cart_total
    
    def get_cart_item(self, obj):
        return obj.get_cart_items
    
class OrderItemSerializer(serializers.ModelSerializer):
        product = serializers.PrimaryKeyRelatedField(queryset=models.Product.objects.all())
        customer = serializers.PrimaryKeyRelatedField(queryset=models.Customer.objects.all())
        size = serializers.PrimaryKeyRelatedField(queryset=models.InventoryModel.objects.all())

        size_label = serializers.CharField(source='size.size', read_only=True)
        product_name = serializers.CharField(source='product.name', read_only=True)
        order_description = serializers.CharField(source='order.description', read_only=True)
        product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)

        class Meta:
            model = models.OrderItem
            fields = [
                'id', 'product', 'size', 'quantity', 'date_added', 'size_label', 'product_name', 'order_description', 'product_price', 'customer'
            ]

        def create(self, validated_data):
            productt = validated_data.get('product')
            size = validated_data.get('size')
            quantity = validated_data.get('quantity')
            customer = validated_data.get('customer')

            if not all([productt, customer, size, quantity]):
                raise serializers.ValidationError("Missing required fields: product, size, quantity, or customer.")

            try:
                inventory_item = models.InventoryModel.objects.get(id=size.id)
            except models.InventoryModel.DoesNotExist:
                raise serializers.ValidationError("Invalid size selection.")

            if inventory_item.quantity < quantity:
                raise serializers.ValidationError('Not enough stock available.')

            inventory_item.quantity -= quantity
            inventory_item.save()

            orderr = models.Order.objects.filter(customer=customer, complete=False).first()

            if not orderr or orderr.complete:
                orderr = models.Order.objects.create(customer=customer)
            orderr.save()


            order_item, created = models.OrderItem.objects.get_or_create(
                product=productt, 
                order=orderr, 
                size=size, 
                defaults={'quantity': quantity}
            )

            if not created:
                order_item.quantity += quantity
                order_item.save()

            return order_item

    
        def delete_order_item(self, pk, id):
                try:
                    order_item = models.OrderItem.objects.get(pk=pk)
                    inventory_item = models.InventoryModel.objects.get(id=id)
                    inventory_item.quantity += order_item.quantity
                    inventory_item.save()
                    order_item.delete()
                    return order_item
                except models.OrderItem.DoesNotExist:
                    raise serializers.ValidationError("Order item not found.")
                except models.InventoryModel.DoesNotExist:
                    raise serializers.ValidationError("Inventory item not found.")

class WishListSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=models.Product.objects.all())
    customer = serializers.PrimaryKeyRelatedField(queryset=models.Customer.objects.all())
    size = serializers.PrimaryKeyRelatedField(queryset=models.InventoryModel.objects.all())

    product_name=serializers.CharField(source='product.name', read_only=True)
    size_name=serializers.CharField(source='size.size', read_only=True)
    product_image = serializers.ImageField(source='product.image_1', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    customer_name=serializers.CharField(source='customer.name', read_only=True)

    class Meta:
        model = models.WishListModel
        fields = [
            'id',
            'product',
            'customer',
            'product_name',
            'customer_name',
            'size',
            'size_name',
            'quantity',
            'product_image',
            'product_price',
            'date_added'
        ]

    
    def create(self, validated_data):
        productt = validated_data.get('product')
        customer = validated_data.get('customer')
        size = validated_data.get('size')
        quantity = validated_data.get('quantity')

        if not all([productt, customer, size, quantity]):
            raise serializers.ValidationError("Missing required fields.")

        if models.WishListModel.objects.filter(product=productt, customer=customer).exists():
            wish_list = models.WishListModel.objects.get(product=productt, customer=customer, size=size)
            wish_list.quantity += quantity
            wish_list.save()
            return wish_list

        wish_list = models.WishListModel(product=productt, customer=customer, size=size, quantity=quantity)
        wish_list.save()
        return wish_list

class MyOrderSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=models.Product.objects.all())
    customer = serializers.PrimaryKeyRelatedField(queryset=models.Customer.objects.all())
    size = serializers.PrimaryKeyRelatedField(queryset=models.InventoryModel.objects.all())

    product_name=serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.ImageField(source='product.image_1', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    customer_name=serializers.CharField(source='customer.name', read_only=True)
    class Meta:
        model = models.MyOrdersModel
        fields = [
            'id',
            'product',
            'customer',
            'size',
            'product_name',
            'customer_name',
            'quantity',
            'product_image',
            'product_price',
            'date_added'
        ]

class ReviewSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=models.Product.objects.all())
    customer = serializers.PrimaryKeyRelatedField(queryset=models.Customer.objects.all(), required=False)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    customer_name = serializers.CharField(source='customer.name', read_only=True)

    class Meta:
        model = models.ReviewModel
        fields = [
            'id',
            'user',
            'customer_name',
            'product',
            'customer',
            'rating',
            'review',
            'date_added',
        ]
    
    def create(self, validated_data):
        product = validated_data.get('product')
        user = validated_data.get('user')
        rating = validated_data.get('rating')
        review_text = validated_data.get('review')

        print(f"Creating or updating review with product: {product}, user: {user}, rating: {rating}, review: {review_text}")

        try:
            customer = models.Customer.objects.get(user=user)
        except models.Customer.DoesNotExist:
            raise NotFound(detail="Customer not found.")
        
        existing_review = models.ReviewModel.objects.filter(user=user, product=product).first()

        if existing_review:
            existing_review.rating = rating
            existing_review.review = review_text
            existing_review.save()
            return existing_review
        else:
            try:
                review_instance = models.ReviewModel.objects.create(
                    user=user,
                    product=product,
                    customer=customer,
                    rating=rating,
                    review=review_text
                )
                return review_instance
            except models.Product.DoesNotExist:
                raise serializers.ValidationError("Product not found.")
            except models.Customer.DoesNotExist:
                raise serializers.ValidationError("Customer not found.")


class ShippingSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = models.ShippingAddress
        fields = '__all__'

    def create(self, validated_data):
        order = validated_data.get('order')
        user_id = validated_data.get('user')
        street = validated_data.get('street')
        city = validated_data.get('city')
        state = validated_data.get('state')
        zipcode = validated_data.get('zipcode')
        country = validated_data.get('country')
        payment = validated_data.get('payment')
        amount = validated_data.get('amount')

        try:
            customer = models.Customer.objects.get(user=user_id)
        except models.Customer.DoesNotExist:
            raise NotFound(detail="Customer not found.")

        shipping_address = models.ShippingAddress.objects.create(
            customer=customer,
            order=order,
            street=street,
            city=city,
            state=state,
            zipcode=zipcode,
            country=country,
            payment=payment,
            amount=amount
        )

        order_items = models.OrderItem.objects.filter(order=order)
        for item in order_items:
            product = item.product
            size = item.size
            quantity = item.quantity
            
            models.MyOrdersModel.objects.get_or_create(
                customer=customer,
                product=product,
                order=order,
                size=size,
                quantity=quantity
            )

        models.OrderItem.objects.filter(order=order).delete()

        return shipping_address


class CancelOrder(serializers.ModelSerializer):
    class Meta:
        model = models.OrderItem
        fields = '__all__'
    
    def delete_order_item(self, pk, id):
        try:
            my_order_item = models.MyOrdersModel.objects.get(pk=pk)
            inventory_item = models.InventoryModel.objects.get(id=id)
            inventory_item.quantity += my_order_item.quantity
            inventory_item.save()

            shipping_addresses = models.ShippingAddress.objects.filter(
                order=my_order_item.order,
                customer=my_order_item.customer
            )

            if not shipping_addresses.exists():
                raise ValidationError("Matching shipping address does not exist.")

            shipping_address = shipping_addresses.latest('date_added')

            shipping_address.amount -= my_order_item.product.price * my_order_item.quantity
            shipping_address.save()

            if shipping_address.amount == 60:
                shipping_address.delete()

            my_order_item.delete()
            return my_order_item
        
        except models.MyOrdersModel.DoesNotExist:
            raise ValidationError("Order item not found.")
        except models.InventoryModel.DoesNotExist:
            raise ValidationError("Inventory item not found.")

        
class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'password2',
        ]

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        return data

    def save(self, **kwargs):
        username = self.validated_data['username']
        first_name = self.validated_data['first_name']
        last_name = self.validated_data['last_name']
        email = self.validated_data['email']
        password = self.validated_data['password']
        
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'Email already exists.'})
        
        account = User(username=username, email=email, first_name=first_name, last_name=last_name)
        account.is_active = False
        account.set_password(password)
        account.save()
        return account
    
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)