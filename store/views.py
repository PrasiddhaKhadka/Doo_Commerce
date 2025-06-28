from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from store.filters import ProductFilter
from store.models import Product, Collection, Review
from store.serializers import ProductSerializer, CollectionSerializer, ReviewSerializer
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination


class CollectionViewSet(ModelViewSet):
     queryset = Collection.objects.annotate(products_count=Count('products')).all()
     serializer_class = CollectionSerializer
     def destroy(self, request, *args, **kwargs):
         collection = get_object_or_404(Collection.objects.annotate(products_count=Count('products')), pk=kwargs['pk'])
         if collection.products.count()>0:
                return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
         collection.delete()
         return super().destroy(request, *args, **kwargs)



class CollectionList(ListCreateAPIView):
    queryset = Collection.objects.annotate(products_count=Count('products')).all() 
    serializer_class = CollectionSerializer


class CollectionDetails(RetrieveUpdateDestroyAPIView):
    queryset = Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class = CollectionSerializer

    def delete(self, request, pk):
         collection = get_object_or_404(Collection.objects.annotate(products_count=Count('products')), pk=pk)
         if collection.products.count()>0:
                return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
         collection.delete()
         return Response(status=status.HTTP_204_NO_CONTENT)




class ProductViewSet(ModelViewSet):
     queryset = Product.objects.all()
     serializer_class = ProductSerializer
     filter_backends = [DjangoFilterBackend, SearchFilter]
     filterset_class = ProductFilter
     search_fields = ['title', 'description']
     ordering_fields = ['price', 'last_update']
     pagination_class = PageNumberPagination


    #  def get_queryset(self):
    #       queryset = Product.objects.all()
    #       collection_id = self.request.query_params.get('collection_id')
    #       if collection_id is not None:
    #            queryset = queryset.filter(collection_id=collection_id)
    #       return queryset

     def destroy(self, request, pk):
          product = get_object_or_404(Product,pk = pk)
          if product.orderitem_set.count()>0:
                return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
          return Response(status=status.HTTP_204_NO_CONTENT)




class ProductList(ListCreateAPIView):
    queryset = Product.objects.select_related('collection').all()
    serializer_class = ProductSerializer

    def get_serializer_context(self):
         return {'request': self.request}

class ProductDetails(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related('collection').all()
    serializer_class = ProductSerializer

    def delete(self, request, pk):
        product = get_object_or_404(Product,pk = pk)
        if product.orderitem_set.count()>0:
                return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

        
class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
         return {
             'product_pk': self.kwargs['product_pk']
         }


    # def get_queryset(self):
    #     return Review.objects.filter(product_id=self.kwargs['product_pk'])