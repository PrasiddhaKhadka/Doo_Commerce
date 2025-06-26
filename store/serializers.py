from rest_framework import serializers
from store.models import Product, Collection
from decimal import Decimal


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

    # collection = CollectionSerializer(read_only=True, many=False,source='collection')
    # collection = serializers.HyperlinkedRelatedField(
    #     queryset=Collection.objects.all(),
    #     view_name='collection_details',
    #     lookup_field='pk',
        
    # )

    def calculate_tax(self, product: Product):
        return product.price * Decimal(1.1)
