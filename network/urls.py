
from django.urls import path
from . import views

urlpatterns = [
    path("login", views.login_view, name="login"),
    path("", views.index, name="index"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path('create_post/', views.create_post_page, name='create_post'),
    path('create_post/submit/', views.create_post, name='create_post_submit'),
    path("like-unlike-post/", views.like_unlike_post, name="like_unlike_post"),
    path("profile/<int:id>/", views.profile, name="profile"),
    path("add-comment/", views.add_comment, name="add_comment"),
    path('like-comment/', views.like_comment, name='like_comment'),
    path('search/', views.search_results, name='search_results'),
    path('post/<int:post_id>/share/',views.share_post, name='share_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),


]
