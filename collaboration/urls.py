from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),

    path("skills/", views.skills, name="skills"),
    path("skill-mapping/", views.skill_mapping, name="skill_mapping"),

    # Opportunity URLs
    path("opportunities/", views.opportunity_list, name="opportunity_list"),
    path("opportunities/create/", views.opportunity_create, name="opportunity_create"),
    path("opportunities/<str:pk>/edit/", views.opportunity_edit, name="opportunity_edit"),
    path("opportunities/<str:pk>/apply/", views.apply_opportunity, name="apply_opportunity"),
    path("opportunities/<str:pk>/", views.opportunity_detail, name="opportunity_detail"),

    # Application URLs
    path("applications/manage/", views.applications_manage, name="applications_manage"),
    path("applications/<str:pk>/update/", views.application_update, name="application_update"),

    # College URLs
    path("college/reports/", views.reports, name="reports"),
    path("skills/delete/<str:pk>/", views.delete_skill, name="delete_skill"),
]