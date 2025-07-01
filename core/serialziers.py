from djoser.serializers import UserSerializer as BaseUserSerializer,  UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers

from core.models import User
from store.models import Customer


class UserCreateSerializer(BaseUserCreateSerializer):
    def save(self, **kwargs):
        user = super().save(**kwargs)
        Customer.objects.create(user=user)



    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']

class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'username', 'email', 'first_name', 'last_name']