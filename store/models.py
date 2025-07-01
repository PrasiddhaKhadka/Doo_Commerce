from django.db import models
from django.core.validators import MinValueValidator
from uuid import uuid4
from django.conf import settings

# Create your models here.
class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['title']
        verbose_name = 'Collection'
        verbose_name_plural = 'Collections'
        app_label = 'store'

    
class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField()
    price = models.DecimalField(max_digits=6, decimal_places=2,validators=[MinValueValidator(1)])
    inventory = models.IntegerField(
        validators=[MinValueValidator(0)]
    )
    # one collection may have many products
    # if realted_name not given then would have => product_set
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT, related_name='products',null=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        app_label = 'store'

    def __str__(self):
        return self.title

class Customer(models.Model):
    MEMBERSHIP_BRONZE = 'B'
    MEMBERSHIP_SILVER = 'S'
    MEMBERSHIP_GOLD = 'G'
    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, 'Bronze'),
        (MEMBERSHIP_SILVER, 'Silver'),
        (MEMBERSHIP_GOLD, 'Gold')
    ]
    phone = models.CharField(max_length=100)
    birth_date = models.DateField(null=True)
    membership = models.CharField(max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.user.first_name} {self.user.last_name}'
    
    class Meta:
        ordering = ['user__first_name', 'user__last_name']
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        app_label = 'store'
        permissions = [
            ('view_history', 'Can view history')
        ]

class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed')
    ]
    placed_at = models.DateTimeField(auto_now_add=True)
    # one customer can have many orders (order_set)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    payment_status = models.CharField(max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        app_label = 'store'
        ordering = ['-placed_at']
        permissions = [
            ('cancel_order', 'Can cancel order')
        ]

    
class OrderItem(models.Model):
    # one order can have many order 
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='order_items')
    # one product can have many order
    # default related name -> <model_name>_ set ==> orderitem_set
    # to access from products => product.orderitem_set
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

class Cart(models.Model):
    customer_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    # one cart can have many cart item
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,related_name='items')
    # one product can be in many cart item
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together=['cart', 'product']



class Address (models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,related_name='addresses')
    zip = models.CharField(max_length=255,null=True)
 

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='reviews')
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)


# class 