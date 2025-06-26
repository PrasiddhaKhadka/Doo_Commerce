from django.urls import path
from . import views


urlpatterns = [
   path('collections/',views.collection_list), 
   path('collections/<int:pk>/',views.collection_details, name='collection_details'),
   path('products/',views.product_list),
   path('products/<int:pk>/',views.product_details),
]
