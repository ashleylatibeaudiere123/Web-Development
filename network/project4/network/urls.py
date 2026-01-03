
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("<str:name>", views.profile, name ="profile"),
    path("<int:id>/following/", views.following, name ="following"),

    #Api paths
    path("edit/<int:id>", views.edit, name="edit"),
    path("likes/<int:id>", views.likes, name="likes")
]
