from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers


router = DefaultRouter()
router.register('products',views.ProductViewSet,basename='products')
router.register('collections',views.CollectionViewSet)
router.register('carts',views.CartViewSet,basename='carts')
router.register('customers',views.CustomerViewSet,basename='customers')
router.register('orders',views.OrderViewSet,basename='orders')

products_router = routers.NestedSimpleRouter(router,'products',lookup='product')
products_router.register('reviews',views.ReviewViewSet,basename='product-reviews')

carts_router = routers.NestedSimpleRouter(router,'carts',lookup='cart')
carts_router.register('items',views.CartItemViewSet,basename='cart-items')

# router.


urlpatterns = router.urls + products_router.urls + carts_router.urls

# urlpatterns = [
#    path('collections/',views.CollectionList.as_view()), 
#    path('collections/<int:pk>/',views.CollectionDetails.as_view()),
#    path('products/',views.ProductList.as_view()),
#    path('products/<int:pk>/',views.ProductDetails.as_view()),
# ]
