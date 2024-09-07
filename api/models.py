from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
RATING =(
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
)
class Color(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=254, unique=True)
    
    def __str__(self):
        return self.name
    
class Size(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=254, unique=True)
    
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=254, unique=True)
    
    def __str__(self):
        return self.name
    
class SubCategory(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=254, unique=True)
    
    def __str__(self):
        return self.name

class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.user.username
    
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField()
    description = models.TextField()
    image_1 = models.ImageField(null=True, blank=True, upload_to='products/')
    image_2 = models.ImageField(null=True, blank=True, upload_to='products/')
    image_3 = models.ImageField(null=True, blank=True, upload_to='products/')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return self.name
    
    @property
    def get_rating(self):
        reviews = self.reviewmodel_set.filter(product=self)
        if reviews.exists():
            total = sum([review.rating for review in reviews])
            rating = total / len(reviews)
            return rating
        return 0

class InventoryModel(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    size = models.ForeignKey(Size, on_delete=models.CASCADE, null=True)
    
    def __str__(self):
        return self.product.name
      
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    status = models.CharField(max_length=254, null=True, blank=False)
    
    def __str__(self):
        return str(self.id)
    
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total
    
    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total
    
    @property
    def get_transaction_id(self):
        return f'{self.id}{self.date_ordered}'
    
class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    size = models.ForeignKey(InventoryModel, on_delete=models.SET_NULL, null=True)
    
    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total
    
    def get_image(self):
        return self.product.image_1.url
    
    # def __str__(self):
    #     return self.product.name

class MyOrdersModel(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    size = models.ForeignKey(InventoryModel, on_delete=models.CASCADE, null=True)
    
    def __str__(self):
        return f'{self.customer.name} - {self.product.name}'
          
class WishListModel(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True, null=True)
    size = models.ForeignKey(InventoryModel, on_delete=models.CASCADE, null=True)
    
    def __str__(self):
        return f'{self.customer.name} - {self.product.name}'

class ReviewModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    rating = models.IntegerField(choices=RATING)
    review = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.product.name} - {self.customer.name}'
    
class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)
    city = models.CharField(max_length=200,null=True)
    street = models.CharField(max_length=200,null=True)
    state = models.CharField(max_length=200,null=True)
    country = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=200,null=True)
    payment = models.CharField(max_length=200, null=True)
    amount = models.IntegerField(null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.city
