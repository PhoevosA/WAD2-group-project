from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed_view, name='feed'),
    path('explore/', views.explore_view, name='explore'),
    path('post/new/', views.create_post_view, name='create_post'),
    path('post/<int:pk>/', views.post_detail_view, name='post_detail'),
    path('post/<int:pk>/edit/', views.edit_post_view, name='edit_post'),
    path('post/<int:pk>/delete/', views.delete_post_view, name='delete_post'),
    path('post/<int:pk>/like/', views.like_toggle_view, name='like_toggle'),
    path('post/<int:pk>/bookmark/', views.bookmark_toggle_view, name='bookmark_toggle'),
    path('comment/<int:pk>/delete/', views.delete_comment_view, name='delete_comment'),
    path('tag/<str:tag_name>/', views.tag_view, name='tag'),
]

