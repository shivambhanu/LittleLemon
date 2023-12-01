from rest_framework.decorators import api_view
from rest_framework.response import Response

#For Token Based Authentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

from rest_framework import generics, permissions, status
from .serializers import MenuItemSerializer, UserSerializer, CartSerializer, OrderItemSerializer, OrderSerializer
from .models import MenuItem, Cart, OrderItem, Order

from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404

from rest_framework.authtoken.models import Token
from datetime import date


###########################---Menu-item endpoints---###########################
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def menuitems_view(request):
    if request.method == 'GET':
        menuitems = MenuItem.objects.all()
        menuitem_serializer = MenuItemSerializer(menuitems, many=True)
        return Response(menuitem_serializer.data, status=status.HTTP_200_OK)
    else:
        if request.user.groups.filter(name="manager").exists():
            menuitem_serializer = MenuItemSerializer(data=request.data)
            if(menuitem_serializer.is_valid()):
                menuitem_serializer.save()
                return Response(menuitem_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(menuitem_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
    

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def edit_menuitems_view(request, pk):
    menuitem_instance = get_object_or_404(MenuItem, pk=pk)
    if request.method == 'GET':
        menuitem_serializer = MenuItemSerializer(menuitem_instance)
        return Response(menuitem_serializer.data)
    else:
        if request.user.groups.filter(name="manager").exists():
            if request.method == 'PUT':
                serializer = MenuItemSerializer(menuitem_instance, data=request.data)
            elif request.method == 'PATCH':
                serializer = MenuItemSerializer(menuitem_instance, data=request.data, partial=True)
            else:
                menuitem_instance.delete()
                return Response(status=status.HTTP_200_OK)
            
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
    



###########################---Group management endpoints---###########################
###########---Group = "manager"---###########
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def manager_view(request):
    if request.user.groups.filter(name="manager").exists():
        manager_group = Group.objects.get(name="manager")
        if request.method == 'POST':
            username = request.data['username']
            user = get_object_or_404(User, username=username)
            manager_group.user_set.add(user)
            return Response({"message": f"{username} added to Managers Group"}, status=status.HTTP_201_CREATED)
        else:
            queryset = manager_group.user_set.all()
            serializer = UserSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_user(request, pk):
    if request.user.groups.filter(name="manager").exists():
        user = get_object_or_404(User, pk=pk)
        manager_group = Group.objects.get(name="manager")
        manager_group.user_set.remove(user)
        return Response({"message": f"Deleted {user.username} successfuly"}, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)




###########################---Delivery Crew---###########################
###########---Group = "delivery-crew"---###########
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def delivery_crew_view(request):
    if request.user.groups.filter(name="manager").exists():
        delivery_group = Group.objects.get(name="delivery-crew")
        if request.method == 'POST':
            username = request.data['username']
            user = get_object_or_404(User, username=username)
            delivery_group.user_set.add(user)
            return Response({"message": f"{username} added to Delivery Crew Group"}, status=status.HTTP_201_CREATED)
        else:
            delivery_guys = delivery_group.user_set.all()
            user_serializer = UserSerializer(delivery_guys, many=True)
            return Response(user_serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_delivery_crew(request, pk):
    if request.user.groups.filter(name="manager").exists():
        user = get_object_or_404(User, pk = pk)
        delivery_group = Group.objects.get(name="delivery-crew")
        delivery_group.user_set.remove(user)
        return Response({"message": f"{user.username} has been removed from Delivery Crew"}, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


###########################---Cart---###########################
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_view(request):
    #fetch the user token
    token = request.auth.key
    token_user = Token.objects.get(key=token)
    # print(token_user.user_id)
    
    if request.method == 'GET':
        cart_objects = Cart.objects.filter(user_id=token_user.user_id)
        cart_serializer = CartSerializer(cart_objects, many=True)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        all_carts = Cart.objects.filter(user_id=token_user.user_id)
        all_carts.delete()
        return Response(status=status.HTTP_200_OK)
        


###########################---Order Management---###########################
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def orders_view(request):
    # token = request.auth.key
    # token_user = Token.objects.get(key=token)
    
    if request.method == 'GET':
        if request.user.groups.filter(name="manager").exists():
            orders = Order.objects.all()
        elif request.user.groups.filter(name="delivery-crew").exists():
            orders = Order.objects.filter(delivery_crew = request.user)
        else:
            orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    else:
        cart_items = Cart.objects.filter(user=request.user)
        cart_list = cart_items.values_list()
        if len(cart_list) == 0:
            return Response({"message": "Your cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        
        sum = 0
        for items in cart_list:
            sum += items[-1]
        
        new_order = Order.objects.create(user=request.user, status=False, total=sum, date=date.today())
        
        for value_dict in cart_items.values():
            menu_item = get_object_or_404(MenuItem, id=value_dict['menuitem_id'])
            order_item = OrderItem.objects.create(order=new_order, menuitem=menu_item, quantity=value_dict['quantity'], unit_price=value_dict['unit_price'], price=value_dict['quantity']*value_dict['unit_price'])
            order_item.save()
            
        cart_items.delete()
        return Response({"message": f"Your new order id is {new_order.pk}. All your items are deleted from cart"}, status.HTTP_201_CREATED)




@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def single_order_view(request, pk):
    
    if request.method == 'GET':
        all_order_items = OrderItem.objects.filter(order_id=pk)
        serializer = OrderItemSerializer(all_order_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        if request.user.groups.filter(name="manager").exists():
            order_instance = get_object_or_404(Order, user_id = pk)
            serializer = OrderSerializer(order_instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(status.HTTP_200_OK)
            return Response(status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status.HTTP_403_FORBIDDEN)
    elif request.method == 'PATCH':
        if request.user.group.filter(name="manager").exists() or request.user.groups.filter(name="delivery-crew").exists():
            order_instance = get_object_or_404(Order, user_id=pk)
            serializer = OrderSerializer(order_instance, data=request.data['status'], partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(status.HTTP_200_OK)
            return Response(status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status.HTTP_403_FORBIDDEN)
    else:
        order_instance = get_object_or_404(Order, user_id=pk)
        order_instance.delete()
        return Response(status.HTTP_200_OK)