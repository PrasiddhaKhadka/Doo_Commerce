from django.contrib import admin
from . import models

# Register your models here.
@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title']
    list_filter = ['title']



@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'price', 'inventory']
    list_editable = ['price']
    list_filter = ['title','price']
    list_per_page = 10
    prepopulated_fields = {'slug': ('title',)}
    
