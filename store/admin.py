from django.contrib import admin,messages
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html
from django.urls import reverse
from . import models


# Register your models here.
@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title','products_count']
    list_filter = ['title']
    search_fields = ['title__istartswith','featured_product__istartswith']
    autocomplete_fields = ['featured_product']

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count = Count('products')
        )

    @admin.display(ordering='products_count')
    def products_count(self, collection: models.Collection):
        url = reverse('admin:store_product_changelist') + f'?collection__id__exact={collection.id}'
        return format_html('<a href="{}">{}</a>',url, collection.products_count)
        # return collection.products_count # type: ignore


# Custom Filter For Product 
class InventoryFilter(admin.SimpleListFilter):
    title = 'Inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            ('<10', 'Low')
        ]
    
    def queryset(self, request, queryset: QuerySet):
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)
        


# INLINE CLASS TO MANAGE TAGS
   

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    # readonly_fields = ['slug']
    autocomplete_fields = ['collection']
    fields = ['title', 'description', 'slug', 'price', 'inventory', 'collection']
    prepopulated_fields = {'slug': ('title',)}
    actions = ['clear_inventory']
    list_display = ['title', 'slug', 'price', 'inventory_status', 'collection__title']
    list_editable = ['price']
    list_filter = ['title','price',InventoryFilter]
    list_per_page = 10
    list_select_related = ['collection']
    search_fields = ['title__istartswith']

    @admin.display(ordering='inventory')
    def inventory_status(self, product: models.Product):
        if product.inventory <= 0:
            return 'Out of Stock'
        else:
            return f'{product.inventory}'
        
    @admin.action(description='Clear Inventory')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(request, f'{updated_count} products were successfully updated',messages.ERROR)


    
@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership','order_count']
    list_editable = ['membership']
    list_select_related = ['user']
    ordering = ['user__first_name', 'user__last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).annotate(
            order_count = Count('order')
        )
    
    def __str__(self) -> str:
        return f'{self.user.first_name} {self.user.last_name}'
    
    
    def first_name(self, customer: models.Customer):
        return customer.user.first_name
    
    def last_name(self, customer: models.Customer):
        return customer.user.last_name
    
    @admin.display(ordering='order_count')
    def order_count(self, order: models.Order):
        return order.order_count
   



class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    extra = 0
    min_num = 1
    max_num = 10
    autocomplete_fields = ['product']

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'placed_at', 'customer','payment_status']
    list_select_related = ['customer']
    search_fields = ['customer__first_name__istartswith', 'customer__last_name__istartswith']
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]


@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = [ 'created_at']

@admin.register(models.CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity']