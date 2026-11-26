from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.utils import timezone
import re

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import (
    UserProfile,
    StudentSkill,
    Opportunity,
    Skill,
    Application
)


# ==========================================
# REGISTRATION FORM
# ==========================================

class RegisterForm(UserCreationForm):

    full_name = forms.CharField(
        max_length=100,
        label="Full Name"
    )

    email = forms.EmailField(required=True)

    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        label="Register As"
    )

    phone = forms.CharField(
        max_length=20,
        required=False,
        label="Phone Number"
    )

    organization = forms.CharField(
        max_length=150,
        required=False,
        label="College / Company / Institution Name"
    )

    course = forms.CharField(
        max_length=100,
        required=False,
        label="Course"
    )

    graduation_year = forms.IntegerField(
        required=False,
        min_value=2000,
        max_value=2100,
        label="Graduation Year"
    )

    designation = forms.CharField(
        max_length=100,
        required=False,
        label="Designation"
    )

    website = forms.URLField(
        required=False,
        label="Website"
    )

    username = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "full_name",
            "role",
            "phone",
            "organization",
            "course",
            "graduation_year",
            "designation",
            "website",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

    def clean_full_name(self):
        name = self.cleaned_data["full_name"].strip()

        if not re.fullmatch(r"[A-Za-z .'-]{2,100}", name):
            raise forms.ValidationError(
                "Enter a valid full name."
            )

        return name

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()

        if not re.fullmatch(r"[+0-9()\-\s]{7,20}", phone):
            raise forms.ValidationError(
                "Enter a valid phone number."
            )

        return phone

    def clean(self):
        cleaned_data = super().clean()

        role = cleaned_data.get("role")
        organization = cleaned_data.get("organization", "").strip()
        phone = cleaned_data.get("phone", "").strip()
        course = cleaned_data.get("course", "").strip()
        graduation_year = cleaned_data.get("graduation_year")
        designation = cleaned_data.get("designation", "").strip()
        website = cleaned_data.get("website")

        # Common validation
        if role and not phone:
            self.add_error(
                "phone",
                "Phone number is required."
            )

        # Student validation
        if role == "student":

            if not organization:
                self.add_error(
                    "organization",
                    "College name is required."
                )

            if not course:
                self.add_error(
                    "course",
                    "Course is required."
                )

            if not graduation_year:
                self.add_error(
                    "graduation_year",
                    "Graduation year is required."
                )

        # Industry validation
        elif role == "industry":

            if not organization:
                self.add_error(
                    "organization",
                    "Company name is required."
                )

            if not designation:
                self.add_error(
                    "designation",
                    "Designation is required."
                )

            if not website:
                self.add_error(
                    "website",
                    "Company website is required."
                )

        # College validation
        elif role == "college":

            if not organization:
                self.add_error(
                    "organization",
                    "Institution name is required."
                )

            if not website:
                self.add_error(
                    "website",
                    "Institution website is required."
                )

        # Generate unique username from email
        email = cleaned_data.get("email")

        if email:
            base = re.sub(
                r"[^A-Za-z0-9_.@+-]",
                "",
                email.split("@")[0]
            )[:25]

            base = base or "user"
            username = base
            counter = 1

            while User.objects.filter(username=username).exists():
                username = f"{base}{counter}"
                counter += 1

            cleaned_data["username"] = username

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        full_name = self.cleaned_data["full_name"].strip()
        name_parts = full_name.split(maxsplit=1)

        user.first_name = name_parts[0]
        user.last_name = (
            name_parts[1] if len(name_parts) > 1 else ""
        )

        if commit:
            user.save()

        return user


# ==========================================
# PROFILE EDIT FORM
# ==========================================

class ProfileForm(forms.ModelForm):

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()

        if phone and not re.fullmatch(
            r"[+0-9()\-\s]{7,20}",
            phone
        ):
            raise forms.ValidationError(
                "Enter a valid phone number (7-20 characters)."
            )

        return phone

    def clean_graduation_year(self):
        year = self.cleaned_data.get("graduation_year")

        if year and not 2000 <= year <= 2100:
            raise forms.ValidationError(
                "Enter a valid graduation year."
            )

        return year

    def clean_resume_link(self):
        value = self.cleaned_data.get("resume_link", "").strip()

        if value and not value.startswith(("https://", "http://")):
            raise forms.ValidationError(
                "Resume link must start with http:// or https://."
            )

        return value

    class Meta:
        model = UserProfile
        fields = [
            "organization",
            "phone",
            "course",
            "graduation_year",
            "bio",
            "resume_link"
        ]

        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3})
        }


# ==========================================
# STUDENT SKILL FORM
# ==========================================

class StudentSkillForm(forms.ModelForm):

    skill_name = forms.CharField(
        max_length=80,
        label="Skill"
    )

    class Meta:
        model = StudentSkill
        fields = ["level"]

    def clean_skill_name(self):
        value = self.cleaned_data["skill_name"].strip()

        if len(value) < 2 or len(value) > 80:
            raise forms.ValidationError(
                "Skill name must be between 2 and 80 characters."
            )

        if not re.fullmatch(r"[A-Za-z0-9+#. /_-]+", value):
            raise forms.ValidationError(
                "Use letters, numbers and common skill symbols only."
            )

        return value


# ==========================================
# OPPORTUNITY FORM
# ==========================================

class OpportunityForm(forms.ModelForm):

    required_skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    def clean_title(self):
        title = self.cleaned_data["title"].strip()

        if len(title) < 4 or len(title) > 150:
            raise forms.ValidationError(
                "Title must be between 4 and 150 characters."
            )

        return title

    def clean_description(self):
        description = self.cleaned_data["description"].strip()

        if len(description) < 30:
            raise forms.ValidationError(
                "Description must contain at least 30 characters."
            )

        return description

    def clean_deadline(self):
        deadline = self.cleaned_data.get("deadline")

        if deadline and deadline < timezone.localdate():
            raise forms.ValidationError(
                "Deadline cannot be in the past."
            )

        return deadline

    class Meta:
        model = Opportunity

        fields = [
            "title",
            "opportunity_type",
            "description",
            "location",
            "stipend_or_salary",
            "duration",
            "required_skills",
            "eligibility",
            "deadline",
            "is_active"
        ]

        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "eligibility": forms.Textarea(attrs={"rows": 3}),
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }


# ==========================================
# APPLICATION STATUS FORM
# ==========================================

class ApplicationStatusForm(forms.ModelForm):

    class Meta:
        model = Application
        fields = ["status"]

class RoleBasedAuthenticationForm(AuthenticationForm):

    role = forms.ChoiceField(
        choices=[
            ("student", "Student"),
            ("industry", "Company / Industry"),
            ("college", "College / Admin"),
        ],
        widget=forms.RadioSelect,
        required=True,
        label="Login as"
    )

    def clean(self):
        cleaned_data = super().clean()

        selected_role = cleaned_data.get("role")
        user = self.get_user()

        if user and selected_role:

            profile = getattr(user, "profile", None)

            if profile is None:
                raise forms.ValidationError(
                    "Your account profile was not found."
                )

            if profile.role != selected_role:
                self.add_error(
                    "role",
                    "The selected role does not match your registered account."
                )

        return cleaned_data
