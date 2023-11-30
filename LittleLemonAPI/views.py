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

# from rest_framework.authtoken.models import Token


###########################---Menu Items---###########################
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
                return Response(status=status.HTTP_204_NO_CONTENT)
            
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
    



###########################---Managers---###########################
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def manager_view(request):
    if request.method == 'POST':
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name="manager")
            managers.user_set.add(user)
            return Response({"message": f"{username} added to Managers Group"})
        else:
            return Response({"message": "Enter the fking username!"})
    else:
        group = Group.objects.get(name="manager")
        queryset = group.user_set.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    managers = Group.objects.get(name="manager")
    managers.user_set.remove(user)
    return Response({"message": f"Deleted {user.username} successfuly"})




###########################---Delivery Crew---###########################
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def delivery_crew_view(request):
    delivery_group = Group.objects.get(name="delivery-crew")
    
    if request.method == 'POST':
        username = request.data['username']
        user = get_object_or_404(User, username=username)
        delivery_group.user_set.add(user)
        return Response({"message": f"{username} added to Delivery Crew Group"})
    else:
        delivery_guys = delivery_group.user_set.all()
        user_serializer = UserSerializer(delivery_guys, many=True)
        return Response(user_serializer.data)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_delivery_crew(request, pk):
    user = get_object_or_404(User, pk = pk)
    delivery_group = Group.objects.get(name="delivery-crew")
    delivery_group.user_set.remove(user)
    return Response({"message": f"{user.username} has been removed from Delivery Crew"})



###########################---Cart---###########################
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_view(request):
    if request.method == 'GET':
        cart_objects = Cart.objects.filter(user_id=request.user.id)
        cart_serializer = CartSerializer(cart_objects, many=True)
        dict = cart_serializer.data
        # for object in dict:
        #     print(get_object_or_404(MenuItem, pk=object['menuitem']))
        return Response(dict)
    elif request.method == 'POST':
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        all_carts = Cart.objects.filter(user_id=request.user.id)
        all_carts.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        


###########################---Order Management---###########################
def orders_view(request):
    orders = Order.objects.filter(user_id=request.user.id)
    
    #Now use orders.id to filter all orderitem from OrderItem model
    order_serializer = OrderItemSerializer(orders, many=True)
    return Response(order_serializer.data)