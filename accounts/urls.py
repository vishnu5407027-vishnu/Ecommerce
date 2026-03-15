from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('add-address/', views.add_address, name='add_address'),
    path('delete-address/<int:id>/', views.delete_address, name='delete_address'),
]


