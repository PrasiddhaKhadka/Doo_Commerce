from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.mixins import  CreateModelMixin,DestroyModelMixin, UpdateModelMixin, RetrieveModelMixin
from store.filters import ProductFilter
from store.models import Cart, Product, Collection, Review, CartItem,Customer, Order
from store.permission import FullDjangoModelPermissions, IsAdminOrReadOnly, ViewCustomerHistoryPermission
from store.serializers import CartSerializer, ProductSerializer, CustomerSerializer, CollectionSerializer, ReviewSerializer, CartItemSerializer,AddCartItemSerializer,UpdateCartItemSerializer, DeleteCartItemSerializer, OrderSerializer,CreateOrderSerializer, UpdateOrderSerializer
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, DjangoModelPermissions


class CollectionViewSet(ModelViewSet):
     queryset = Collection.objects.annotate(products_count=Count('products')).all()
     serializer_class = CollectionSerializer
     filter_backends = [DjangoFilterBackend, SearchFilter]
     permission_classes = [IsAdminOrReadOnly]
     def destroy(self, request, *args, **kwargs):
         collection = get_object_or_404(Collection.objects.annotate(products_count=Count('products')), pk=kwargs['pk'])
         if collection.products.count()>0:
                return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
         collection.delete()
         return super().destroy(request, *args, **kwargs)





class ProductViewSet(ModelViewSet):
     queryset = Product.objects.all()
     serializer_class = ProductSerializer
     filter_backends = [DjangoFilterBackend, SearchFilter]
     filterset_class = ProductFilter
     search_fields = ['title', 'description']
     ordering_fields = ['price', 'last_update']
     pagination_class = PageNumberPagination
     permission_classes = [IsAdminOrReadOnly]
     def destroy(self, request, pk):
          product = get_object_or_404(Product,pk = pk)
          if product.orderitem_set.count()>0:
                return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
          return Response(status=status.HTTP_204_NO_CONTENT)




        
class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
         return {
             'product_pk': self.kwargs['product_pk']
         }



class CartViewSet(CreateModelMixin,RetrieveModelMixin, DestroyModelMixin,GenericViewSet):
     queryset = Cart.objects.prefetch_related('items__product').all()
     serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
     # serializer_class = CartItemSerializer
     http_method_names = ['get', 'post', 'patch', 'delete']

     def get_serializer_class(self):
          if self.request.method == 'POST':
               return AddCartItemSerializer
          elif self.request.method == 'PATCH':
               return UpdateCartItemSerializer
          elif self.request.method == 'DELETE':
               return DeleteCartItemSerializer
          
          return CartItemSerializer
     
     def get_serializer_context(self):
          return {
               'cart_pk': self.kwargs['cart_pk']
          }

     def get_queryset(self):
          return CartItem.objects.select_related('product').filter(cart_id=self.kwargs['cart_pk'])
      

class CustomerViewSet(ModelViewSet):
     queryset = Customer.objects.all()
     serializer_class = CustomerSerializer
     permission_classes = [IsAdminUser]

     @action(detail=True, methods=['GET'],permission_classes=[ViewCustomerHistoryPermission])
     def history(self, request, pk):
          return Response('ok')

     @action(detail=False, methods=['GET', 'PUT', 'PATCH'] , permission_classes=[IsAuthenticated])
     def me(self, request):
          customer = Customer.objects.get(user_id=request.user.id)
          if request.method == 'GET':
               serializer = CustomerSerializer(customer)
               return Response(serializer.data)
          elif request.method == 'PUT':
               serializer = CustomerSerializer(customer, data=request.data)
               serializer.is_valid(raise_exception=True)
               serializer.save()
               return Response(serializer.data)
          elif request.method == 'PATCH':
               serializer = CustomerSerializer(customer, data=request.data, partial=True)
               serializer.is_valid(raise_exception=True)
               serializer.save()
               return Response(serializer.data)
          # (customer) = Customer.objects.get_or_create(user_id=request.user.id)
          # serializer = CustomerSerializer(customer) 
          # return Response(serializer.data)



class OrderViewSet(ModelViewSet):
     # serializer_class = OrderSerializer

     http_method_names = ['get','post', 'patch', 'delete', 'head','options']
     def get_permissions(self):
          if self.request.method in ['PATCH', 'DELETE']:
               return [IsAdminUser()]
          return [IsAuthenticated()]
     
     def create(self, request, *args, **kwargs):
          serializer = CreateOrderSerializer(data=request.data, context={'user_id': self.request.user.id})
          serializer.is_valid(raise_exception=True)
          order = serializer.save()
          serializer = OrderSerializer(order)
          return Response(serializer.data)

     def get_serializer_class(self, *args, **kwargs):
          if self.request.method == 'POST':
               return CreateOrderSerializer
          elif self.request.method == 'PATCH':
               return UpdateOrderSerializer
          return OrderSerializer
     

     def get_serializer_context(self):
          return {
               'user_id': self.request.user.id
          }

     def get_queryset(self):
          if self.request.user.is_staff:
               return Order.objects.all()
          customer_id =  Order.objects.only('id') .get(user_id = self.request.user.id)
          return Order.objects.filter(customer_id = customer_id)
