from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserProfileEditForm
from .models import Status
from datetime import date
from user_management.models import WeightHistory

def register_view(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('log_activity')

    form = UserRegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully. You can now log in.")
            return redirect('login')
        else:
            # Show detailed field errors
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, f"{error}")
                    else:
                        messages.error(request, f"{field.capitalize()}: {error}")
    return render(request, 'user_management/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('log_activity')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect('log_activity')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'user_management/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

@login_required
def profile_view(request):
    user = request.user
    bmi_status = Status.objects.filter(min_bmi__lte=user.bmi, max_bmi__gte=user.bmi).first()

    bmi_result = None
    bmi_calc_status = None
    error_msg = None

    entered_weight = ""
    entered_height = ""

    if request.method == "POST":
        entered_weight = request.POST.get("calc_weight", "")
        entered_height = request.POST.get("calc_height", "")

        try:
            weight = float(entered_weight)
            height = float(entered_height)

            if weight <= 0 or height <= 0:
                error_msg = "Please enter positive values for both weight and height."
            elif weight > 500 or height > 3:
                error_msg = "Please check your input."
            else:
                bmi_result = round(weight / (height ** 2), 2)
                bmi_calc_status = Status.objects.filter(
                    min_bmi__lte=bmi_result, max_bmi__gte=bmi_result
                ).first()
        except ValueError:
            error_msg = "Invalid input. Please enter numeric values only."

    return render(request, 'user_management/profile.html', {
        'user_obj': user,
        'bmi_status': bmi_status,
        'bmi_result': bmi_result,
        'bmi_calc_status': bmi_calc_status,
        'error_msg': error_msg,
        'entered_weight': entered_weight,
        'entered_height': entered_height,
    })

@login_required
def profile_edit(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileEditForm(request.POST, instance=user)
        if form.is_valid():
            previous_weight = user.weight
            updated_user = form.save()

            # Sync to WeightHistory only if weight has changed
            if updated_user.weight != previous_weight:
                WeightHistory.objects.update_or_create(
                    user=updated_user,
                    recorded_at=date.today(),
                    defaults={'weight_kg': updated_user.weight}
                )
            messages.success(request, "Your profile has been updated.")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserProfileEditForm(instance=user)
    return render(request, 'user_management/profile_edit.html', {'form': form})