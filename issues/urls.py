from django.urls import path
from . import views

app_name = "issues"

urlpatterns = [
    # Home
    path("", views.home, name="home"),

    # Auth / user
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),

    # Complaints
    path("complaints/", views.complaint_list, name="complaint_list"),
    path("complaints/create/", views.create_complaint, name="create_complaint"),
    path("complaints/mine/", views.my_complaints, name="my_complaints"),
    path("my_complaints/", views.my_complaints, name="my_complaints_short"),
    path("complaints/<int:pk>/", views.view_complaint, name="view_complaint"),

    # Search / API
    path("search/", views.search, name="search"),
    path("api/unread/", views.unread_count_api, name="unread_count_api"),

    # Admin
    path("admin/complaints/", views.admin_complaints, name="admin_complaints"),
    path("admin/complaints/<int:pk>/update/", views.admin_update_complaint, name="admin_update_complaint"),
]