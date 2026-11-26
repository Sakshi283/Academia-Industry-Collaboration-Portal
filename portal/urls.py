from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView

from collaboration import views
from collaboration.forms import RoleBasedAuthenticationForm


urlpatterns = [
    path("admin/", admin.site.urls),

    path("", views.home, name="home"),

    # Custom role-based login
    path(
        "accounts/login/",
        LoginView.as_view(
            authentication_form=RoleBasedAuthenticationForm,
            template_name="registration/login.html"
        ),
        name="login"
    ),

    # Other authentication URLs
    path("accounts/", include("django.contrib.auth.urls")),

    path("", include("collaboration.urls")),
]