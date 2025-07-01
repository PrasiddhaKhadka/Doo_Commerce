from rest_framework import serializers
from store.models import Cart, CartItem, Product, Collection, Customer,  Review, Order, OrderItem
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.db import transaction
from .signals import order_created



class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title','products_count']

    products_count = serializers.IntegerField(read_only=True)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'price', 'inventory','price_with_tax', 'collection']

    price_with_tax = serializers.SerializerMethodField('calculate_tax')

    def calculate_tax(self, product: Product):
        return product.price * Decimal(1.1)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'name', 'description', 'date']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)
    

class ProductSerializerForCart(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price']


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializerForCart()
    total_price = serializers.SerializerMethodField('calculate_total_price')

    def calculate_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.price

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity','total_price']
        
    
class CartSerializer(serializers.ModelSerializer):
    customer_id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField('calculate_total_price')

    def calculate_total_price(self, cart: Cart):
        return sum([item.quantity * item.product.price for item in cart.items.all()])
    class Meta:  
        model= Cart
        fields= ['customer_id', 'items','total_price']





class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No product with the given ID was found.')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_pk']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try: 
            cart_item= CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

class DeleteCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id']


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone', 'birth_date', 'membership']

    def update(self, instance, validated_data):
        validated_data.pop('user', None)  # don't allow user to be updated
        return super().update(instance, validated_data)
    
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializerForCart()
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True,read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'placed_at', 'customer','payment_status', 'order_items']


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError('No cart with the given ID was found.')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('The cart is empty.')
        return cart_id
    
    def save(self,**kwargs):
        with transaction.atomic():
            customer = Customer.objects.get(user_id=self.context['user_id'])
            order=  Order.objects.create(
            customer = customer
            )

            cart_items= CartItem.objects.select_related('product').filter(cart_id=self.validated_data['cart_id'])
            order_items = [
                OrderItem(
                order = order,
                product = items.product,
                quantity = items.quantity,
                price = items.product.price

            ) for items in cart_items]

            OrderItem.objects.bulk_create(order_items)
            Cart.objects.filter(pk=self.validated_data['cart_id']).delete()

            order_created.send_robust(sender=self.__class__, order=order)
            
            return order


