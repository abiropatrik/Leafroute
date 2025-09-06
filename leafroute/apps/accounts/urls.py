from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import CustomAuthenticationForm

from . import views

app_name = 'account'
urlpatterns = [
    path('accounts/profile',views.ProfileView.as_view(),name="profile"),

    # Django Auth
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name="accounts/login.html",
        authentication_form=CustomAuthenticationForm
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(template_name="accounts/logout.html"), name='logout'),
]