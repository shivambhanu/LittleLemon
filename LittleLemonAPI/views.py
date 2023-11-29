from rest_framework.decorators import api_view
from rest_framework.response import Response

#For Token Based Authentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

from rest_framework import generics, permissions, status
from .serializers import MenuItemSerializer, UserSerializer, CartSerializer
from .models import MenuItem, Cart

from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404

from rest_framework.authtoken.models import Token


###########################---Menu Items---###########################
class MenuItemsView(generics.ListCreateAPIView, generics.RetrieveAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()
        

class EditMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method != 'GET':
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()



###########################---Managers---###########################
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAdminUser])
def manager_view(request):
    if request.method == 'POST':
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name="Manager")
            managers.user_set.add(user)
            return Response({"message": f"{username} added to Managers Group"})
        else:
            return Response({"message": "Enter the fking username!"})
    else:
        group = Group.objects.get(name="Manager")
        queryset = group.user_set.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([permissions.IsAdminUser])
def remove_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    managers = Group.objects.get(name="Manager")
    managers.user_set.remove(user)
    return Response({"message": f"Deleted {user.username} successfuly"})




###########################---Delivery Crew---###########################
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAdminUser])
def delivery_crew_view(request):
    delivery_group = Group.objects.get(name="Delivery Crew")
    
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
@permission_classes([permissions.IsAdminUser])
def remove_delivery_crew(request, pk):
    user = get_object_or_404(User, pk = pk)
    delivery_group = Group.objects.get(name="Delivery Crew")
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
