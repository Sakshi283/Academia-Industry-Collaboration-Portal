from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import re
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("college", "College/Admin"),
        ("industry", "Industry/Company"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    organization = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    course = models.CharField(max_length=100, blank=True)
    graduation_year = models.PositiveIntegerField(null=True, blank=True)
    bio = models.TextField(blank=True)
    resume_link = models.URLField(blank=True)

    def clean(self):
        errors = {}
        if self.phone and not re.fullmatch(r"[+0-9()\\-\\s]{7,20}", self.phone):
            errors["phone"] = "Enter a valid phone number (7–20 characters)."
        if self.graduation_year and not 2000 <= self.graduation_year <= 2100:
            errors["graduation_year"] = "Enter a year between 2000 and 2100."
        if self.role == "student" and self.graduation_year is None:
            # Graduation year is optional while registering; profile completion can add it later.
            pass
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Skill(models.Model):
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ["name"]

    def clean(self):
        self.name = (self.name or "").strip()
        if len(self.name) < 2:
            raise ValidationError({"name": "Skill name must contain at least 2 characters."})
        if len(self.name) > 80:
            raise ValidationError({"name": "Skill name cannot exceed 80 characters."})

    def __str__(self):
        return self.name


class StudentSkill(models.Model):
    LEVELS = [("Beginner", "Beginner"), ("Intermediate", "Intermediate"), ("Advanced", "Advanced")]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student_skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    level = models.CharField(max_length=20, choices=LEVELS, default="Beginner")

    class Meta:
        unique_together = ("student", "skill")

    def clean(self):
        if self.student_id and getattr(getattr(self.student, "profile", None), "role", None) != "student":
            raise ValidationError({"student": "Only student accounts can add skills."})

    def __str__(self):
        return f"{self.student.username} - {self.skill.name}"


class Opportunity(models.Model):
    TYPES = [("internship", "Internship"), ("job", "Placement / Job")]
    title = models.CharField(max_length=150)
    company = models.ForeignKey(User, on_delete=models.CASCADE, related_name="opportunities")
    opportunity_type = models.CharField(max_length=20, choices=TYPES)
    description = models.TextField()
    location = models.CharField(max_length=120, blank=True)
    stipend_or_salary = models.CharField(max_length=100, blank=True)
    duration = models.CharField(max_length=100, blank=True)
    required_skills = models.ManyToManyField(Skill, blank=True, related_name="opportunities")
    eligibility = models.TextField(blank=True)
    deadline = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        errors = {}
        self.title = (self.title or "").strip()
        if len(self.title) < 4:
            errors["title"] = "Title must contain at least 4 characters."
        if len(self.description or "") < 30:
            errors["description"] = "Please provide at least 30 characters of description."
        if self.deadline and self.deadline < timezone.localdate():
            errors["deadline"] = "Deadline cannot be in the past."
        if self.company_id and getattr(getattr(self.company, "profile", None), "role", None) != "industry":
            errors["company"] = "Only industry accounts can publish opportunities."
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return self.title


class Application(models.Model):
    STATUSES = [
        ("Applied", "Applied"),
        ("Under Review", "Under Review"),
        ("Shortlisted", "Shortlisted"),
        ("Rejected", "Rejected"),
        ("Selected", "Selected"),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications")
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name="applications")
    status = models.CharField(max_length=20, choices=STATUSES, default="Applied")
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "opportunity")
        ordering = ["-applied_at"]

    def clean(self):
        errors = {}
        if self.student_id and getattr(getattr(self.student, "profile", None), "role", None) != "student":
            errors["student"] = "Only student accounts can apply."
        if self.opportunity_id and not self.opportunity.is_active:
            errors["opportunity"] = "This opportunity is closed."
        if self.student_id and self.opportunity_id and self.student_id == self.opportunity.company_id:
            errors["student"] = "A company cannot apply to its own opportunity."
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.student.username} -> {self.opportunity.title}"
