from django.urls import path
from . import views
# from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # path('secret', views.secret),
    # path('api-token-auth', obtain_auth_token),
    # path('manager-view', views.manager_view),
    
    path('menu-items', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>', views.EditMenuItemView.as_view()),
    
    path('groups/manager/users', views.manager_view),
    path('groups/manager/users/<int:pk>', views.remove_user),
    
    path('groups/delivery-crew/users', views.delivery_crew_view),
    path('groups/delivery-crew/users/<int:pk>', views.remove_delivery_crew),
]
