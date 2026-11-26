from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import (
    UserProfile,
    Skill,
    StudentSkill,
    Opportunity,
    Application
)

from .forms import (
    RegisterForm,
    ProfileForm,
    StudentSkillForm,
    OpportunityForm,
    ApplicationStatusForm
)

from .decorators import role_required


# ---------------- HOME PAGE ----------------

def home(request):
    student_count = sum(
        1 for profile in UserProfile.objects.filter(role="student")
        if User.objects.filter(pk=profile.user_id).exists()
    )

    company_count = sum(
        1 for profile in UserProfile.objects.filter(role="industry")
        if User.objects.filter(pk=profile.user_id).exists()
    )

    stats = {
        "students": student_count,
        "companies": company_count,
        "opportunities": Opportunity.objects.filter(is_active=True).count(),
    }

    return render(request, "collaboration/home.html", {"stats": stats})

# ---------------- REGISTRATION ----------------

def register(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save()

            UserProfile.objects.create(
                user=user,
                role=form.cleaned_data["role"],
                organization=form.cleaned_data.get("organization", ""),
                phone=form.cleaned_data.get("phone", ""),
                course=form.cleaned_data.get("course", ""),
                graduation_year=form.cleaned_data.get("graduation_year"),
                designation=form.cleaned_data.get("designation", ""),
                website=form.cleaned_data.get("website", ""),
            )

            login(request, user)

            messages.success(
                request,
                "Your account has been created successfully."
            )

            return redirect("dashboard")

    else:
        form = RegisterForm()

    return render(
        request,
        "registration/register.html",
        {"form": form}
    )


# ---------------- DASHBOARD ----------------

@login_required
def dashboard(request):

    profile = getattr(request.user, "profile", None)

    if profile is None:
        messages.error(
            request,
            "Your profile is incomplete. Please contact the administrator."
        )
        return redirect("home")

    context = {
        "profile": profile
    }

    # STUDENT DASHBOARD
    if profile.role == "student":

        context.update({
            "my_skills": StudentSkill.objects.filter(
                student=request.user
            ),

            "applications": Application.objects.filter(
                student=request.user
            ),

            "recommended": Opportunity.objects.filter(
                is_active=True
            )[:5],

            "skill_count": StudentSkill.objects.filter(
                student=request.user
            ).count(),
        })

        return render(
            request,
            "collaboration/student_dashboard.html",
            context
        )

    # INDUSTRY DASHBOARD
    if profile.role == "industry":

        context.update({
            "opportunities": Opportunity.objects.filter(
                company=request.user
            ),

            "application_count": Application.objects.filter(
                opportunity__company=request.user
            ).count(),
        })

        return render(
            request,
            "collaboration/industry_dashboard.html",
            context
        )

    # COLLEGE DASHBOARD
    context.update({
       "student_count": sum(
    1 for profile in UserProfile.objects.filter(role="student")
    if User.objects.filter(pk=profile.user_id).exists()
),

        "company_count": sum(
    1 for profile in UserProfile.objects.filter(role="industry")
    if User.objects.filter(pk=profile.user_id).exists()
),

        "opportunity_count": Opportunity.objects.filter(
            is_active=True
        ).count(),

        "applications": Application.objects.all()[:10],

        "students": UserProfile.objects.filter(
            role="student"
        ),
    })

    return render(
        request,
        "collaboration/college_dashboard.html",
        context
    )


# ---------------- EDIT PROFILE ----------------

@login_required
def profile_edit(request):

    profile = request.user.profile

    if request.method == "POST":

        form = ProfileForm(
            request.POST,
            instance=profile
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Profile updated successfully."
            )

            return redirect("dashboard")

    else:
        form = ProfileForm(instance=profile)

    return render(
        request,
        "collaboration/form_page.html",
        {
            "form": form,
            "heading": "Edit profile",
            "button": "Save profile"
        }
    )


# ---------------- STUDENT SKILLS ----------------



@login_required
@role_required("student")
def skills(request):

    if request.method == "POST":

        form = StudentSkillForm(request.POST)

        if form.is_valid():

            name = form.cleaned_data["skill_name"].strip()

            # Reuse an existing skill or create a new one
            skill = Skill.objects.filter(name=name).first()

            if skill is None:
                skill = Skill.objects.filter(
                    name__iexact=name
                ).first()

            if skill is None:
                skill, created_skill = Skill.objects.get_or_create(
                    name=name
                )

            # Add skill to the student's profile
            student_skill, created = StudentSkill.objects.get_or_create(
                student=request.user,
                skill=skill,
                defaults={
                    "level": form.cleaned_data["level"]
                }
            )

            if not created:
                student_skill.level = form.cleaned_data["level"]
                student_skill.save()

            messages.success(
                request,
                f"{skill.name} added to your skills."
            )

            return redirect("skills")

    else:
        form = StudentSkillForm()

    items = StudentSkill.objects.filter(
        student=request.user
    )

    return render(
        request,
        "collaboration/skills.html",
        {
            "form": form,
            "items": items
        }
    )

# ---------------- SKILL MAPPING ----------------

@login_required
@role_required("student")
def skill_mapping(request):

    my_skill_ids = set(
        StudentSkill.objects.filter(
            student=request.user
        ).values_list("skill_id", flat=True)
    )

    opportunities = Opportunity.objects.filter(
        is_active=True
    )

    results = []

    for opportunity in opportunities:

        required = list(
            opportunity.required_skills.all()
        )

        required_ids = {
            skill.id for skill in required
        }

        matched = [
            skill.name
            for skill in required
            if skill.id in my_skill_ids
        ]

        missing = [
            skill.name
            for skill in required
            if skill.id not in my_skill_ids
        ]

        if required:
            percent = round(
                (len(matched) / len(required)) * 100
            )
        else:
            percent = 0

        results.append({
            "opportunity": opportunity,
            "matched": matched,
            "missing": missing,
            "percent": percent,
        })

    results.sort(
        key=lambda x: x["percent"],
        reverse=True
    )

    return render(
        request,
        "collaboration/skill_mapping.html",
        {"results": results}
    )


# ---------------- OPPORTUNITY LIST ----------------

def opportunity_list(request):

    opportunities = Opportunity.objects.filter(
        is_active=True
    )

    kind = request.GET.get("type")

    if kind in ("internship", "job"):

        opportunities = opportunities.filter(
            opportunity_type=kind
        )

    return render(
        request,
        "collaboration/opportunity_list.html",
        {
            "opportunities": opportunities,
            "selected_type": kind
        }
    )


# ---------------- OPPORTUNITY DETAILS ----------------

def opportunity_detail(request, pk):

    opportunity = get_object_or_404(
        Opportunity,
        pk=pk,
        is_active=True
    )

    applied = (
        request.user.is_authenticated
        and Application.objects.filter(
            student=request.user,
            opportunity=opportunity
        ).exists()
    )

    return render(
        request,
        "collaboration/opportunity_detail.html",
        {
            "opportunity": opportunity,
            "applied": applied
        }
    )


# ---------------- CREATE OPPORTUNITY ----------------

@login_required
@role_required("industry")
def opportunity_create(request):

    if request.method == "POST":

        form = OpportunityForm(request.POST)

        if form.is_valid():

            opportunity = form.save(commit=False)

            opportunity.company = request.user

            opportunity.full_clean()
            opportunity.save()

            form.save_m2m()

            messages.success(
                request,
                "Opportunity published successfully."
            )

            return redirect("dashboard")

    else:
        form = OpportunityForm()

    return render(
        request,
        "collaboration/form_page.html",
        {
            "form": form,
            "heading": "Post an opportunity",
            "button": "Publish"
        }
    )


# ---------------- EDIT OPPORTUNITY ----------------

@login_required
@role_required("industry")
def opportunity_edit(request, pk):

    opportunity = get_object_or_404(
        Opportunity,
        pk=pk,
        company=request.user
    )

    if request.method == "POST":

        form = OpportunityForm(
            request.POST,
            instance=opportunity
        )

        if form.is_valid():

            opportunity = form.save(commit=False)

            opportunity.full_clean()
            opportunity.save()

            form.save_m2m()

            messages.success(
                request,
                "Opportunity updated successfully."
            )

            return redirect("dashboard")

    else:
        form = OpportunityForm(instance=opportunity)

    return render(
        request,
        "collaboration/form_page.html",
        {
            "form": form,
            "heading": "Edit opportunity",
            "button": "Save changes"
        }
    )


# ---------------- MANAGE APPLICATIONS ----------------

@login_required
@role_required("industry")
def applications_manage(request):

    applications = Application.objects.filter(
        opportunity__company=request.user
    )

    return render(
        request,
        "collaboration/applications_manage.html",
        {"applications": applications}
    )


# ---------------- UPDATE APPLICATION STATUS ----------------

@login_required
@role_required("industry")
def application_update(request, pk):

    application = get_object_or_404(
        Application,
        pk=pk,
        opportunity__company=request.user
    )

    if request.method == "POST":

        form = ApplicationStatusForm(
            request.POST,
            instance=application
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Application status updated successfully."
            )

    return redirect("applications_manage")


# ---------------- APPLY FOR OPPORTUNITY ----------------

@login_required
@role_required("student")
def apply_opportunity(request, pk):

    opportunity = get_object_or_404(
        Opportunity,
        pk=pk,
        is_active=True
    )

    if request.method == "POST":

        application, created = Application.objects.get_or_create(
            student=request.user,
            opportunity=opportunity
        )

        if created:

            messages.success(
                request,
                "Application submitted successfully."
            )

        else:

            messages.info(
                request,
                "You have already applied for this opportunity."
            )

    return redirect(
        "opportunity_detail",
        pk=pk
    )


# ---------------- COLLEGE REPORTS ----------------
# ---------------- COLLEGE REPORTS ----------------

@login_required
@role_required("college")
def reports(request):

    students = UserProfile.objects.filter(
        role="student"
    )

    student_data = []

    for profile in students:

        # Check whether the linked User actually exists
        try:
            user = profile.user
        except User.DoesNotExist:
            continue

        skill_count = StudentSkill.objects.filter(
            student=user
        ).count()

        application_count = Application.objects.filter(
            student=user
        ).count()

        student_data.append({
            "profile": profile,
            "user": user,
            "skill_count": skill_count,
            "application_count": application_count
        })

    return render(
        request,
        "collaboration/reports.html",
        {
            "student_data": student_data
        }
    )

@login_required
@role_required("student")
def delete_skill(request, pk):
    student_skill = get_object_or_404(
        StudentSkill,
        pk=pk,
        student=request.user
    )

    if request.method == "POST":
        student_skill.delete()
        messages.success(request, "Skill removed from your profile.")

    return redirect("skills")