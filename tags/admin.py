from django.contrib import admin
from django.db.models.query import QuerySet
from django.db.models import Count
from django.http import HttpRequest
from . import models

# Register your models here.
@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']


    # def get_queryset(self, request):
    #     return super().get_queryset(request).annotate(
    #         tagged_items_count= Count('taggeditems')
    #     )
    

    # def tagged_items_count(self, tag: models.Tag):
    #     return tag.tagged_items_count
    