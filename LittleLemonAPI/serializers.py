from rest_framework import serializers
from .models import MenuItem, Cart, OrderItem, Order
from django.contrib.auth.models import User, Group


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['title', 'price', 'featured', 'category']
        
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"
  
        
        
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order 
        fields = "__all__"
        
        
class OrderItemSerializer(serializers.ModelSerializer):
    order = OrderSerializer()
    class Meta:
        model = OrderItem
        fields = "__all__"