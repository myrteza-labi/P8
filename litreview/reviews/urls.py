from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.feed, name='feed'),
    path('ticket/create/', views.create_ticket, name='create_ticket'),
    path('review/create/', views.create_review, name='create_review'),
    path('ticket/<int:ticket_id>/edit/', views.edit_ticket, name='edit_ticket'),
    path('ticket/<int:ticket_id>/delete/', views.delete_ticket, name='delete_ticket'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('follow/', views.follow_user, name='follow_user'),
    path('followed_users/', views.view_followed_users, name='view_followed_users'),
    path('posts/', views.view_posts, name='posts'),
    path('review/create/<int:ticket_id>/', views.create_review_for_ticket, name='create_review_for_ticket'),
    path('unfollow/<int:follow_id>/', views.unfollow_user, name='unfollow_user'),
    path('followed_users/', views.view_followed_users, name='view_followed_users'),
]
