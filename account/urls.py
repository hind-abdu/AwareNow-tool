from django.urls import path
from . import views

app_name = 'account'
urlpatterns = [
    path("login/", views.platform_login, name="platform-login"),
    path("dashboard/", views.platform_dashboard, name="platform-dashboard"),
    path("companies/create/", views.create_company, name="create-company"),
    path(
    "companies/<int:company_id>/super-admin/",
    views.create_super_admin,
    name="create-super-admin"
    ),
    path("logout/", views.logout_view, name="logout"),
]