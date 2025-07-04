from django.contrib import admin

from store.models import Product
from . import models
from store.admin import ProductAdmin
from tags.models import TaggedItem
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.
@admin.register(models.User)
class UserAdmin(BaseUserAdmin):
  
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "usable_password", "password1", "password2","email", "first_name", "last_name"),
            },
        ),
    )



class TagInline(GenericTabularInline):
    model =  TaggedItem
    extra = 0
    max_num = 10
    min_num = 1
    autocomplete_fields = ['tag']
    
class CustomProductAdmin(ProductAdmin):
    inlines = [TagInline]

admin.site.unregister(Product)
admin.site.register(Product, CustomProductAdmin)