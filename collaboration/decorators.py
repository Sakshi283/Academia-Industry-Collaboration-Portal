from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect

def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            profile = getattr(request.user, "profile", None)
            if not request.user.is_authenticated:
                return redirect("login")
            if profile is None or profile.role not in roles:
                messages.error(request, "You do not have permission to access that page.")
                return redirect("dashboard")
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator
