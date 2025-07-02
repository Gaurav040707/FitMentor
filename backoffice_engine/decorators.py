from django.shortcuts import redirect
from functools import wraps
from .models import User_health


def session_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get("id"):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view



def bmi_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user_id = request.session.get("id")
        if not user_id:
            # Not even logged in
            return redirect('login')

        # If they haven’t submitted any health data yet…
        if not User_health.objects.filter(user_id=user_id).exists():
            # Redirect them to the BMI form to enter their metrics
            return redirect('bmi')   # or use reverse('bmi') / url name you’ve set

        # All good—let them proceed
        return view_func(request, *args, **kwargs)

    return _wrapped_view