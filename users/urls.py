from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('profile/<str:username>/followers/', views.followers_view, name='followers'),
    path('profile/<str:username>/following/', views.following_view, name='following'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    path('delete-account/', views.delete_account_view, name='delete_account'),
    path('follow/<str:username>/', views.follow_toggle_view, name='follow_toggle'),
    path('bookmarks/', views.bookmarks_view, name='bookmarks'),
]