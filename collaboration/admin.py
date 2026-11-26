from django.contrib import admin
from .models import UserProfile, Skill, StudentSkill, Opportunity, Application

admin.site.register(UserProfile)
admin.site.register(Skill)
admin.site.register(StudentSkill)

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "opportunity_type", "is_active", "created_at")
    list_filter = ("opportunity_type", "is_active")
    search_fields = ("title", "company__username")

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("student", "opportunity", "status", "applied_at")
    list_filter = ("status",)
