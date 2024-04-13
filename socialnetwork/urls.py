from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login", views.login_view, name="login"),
    path("register", views.register_view, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("course/<str:playlist_id>", views.course_view, name="course"),
    path("profile/<str:username>", views.profile_view, name="profile"),
    path('follow/<str:username>/', views.follow, name='follow'),
    path('unfollow/<str:username>/', views.unfollow, name='unfollow'),
]
