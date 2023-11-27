from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

#For Token Based Authentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

from rest_framework import generics, permissions
from .serializers import MenuItemSerializer
from .models import MenuItem

from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from rest_framework import status



# Create your views here.
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def secret(request):
#     return Response({"message": "This is a secret message."})


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def manager_view(request):
#     if request.user.groups.filter(name="Manager").exists():
#         return Response({"message": "Welcome Mr. Manager"})
#     else:
#         return Response({"message": "You are not authorized"}, 404)



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



@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAdminUser])
def managers(request):
    username = request.data['username']
    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name="Manager")
        if request.method == 'POST':
            managers.user_set.add(user)
            return Response({"message": f"{username} added to Managers Group"})
        else:
            data = list(Group.objects.all().filter(name="Manager").values())
            return Response(data)
    return Response({"message": "error"}, status.HTTP_400_BAD_REQUEST)



class GroupManagerView(generics.ListCreateAPIView):
    





@api_view(['DELETE'])
@permission_classes([permissions.IsAdminUser])
def remove_user(request):
    username = request.data['username']
    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name="Manager")
        managers.user_set.remove(user)
        return Response({"message": f"Deleted {username} successfuly"})
    return Response({"message": "error"}, status.HTTP_404_BAD_REQUEST)

