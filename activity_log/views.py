from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Max
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from .forms import ActivityLogForm
from .models import ActivityLog
from user_management.models import WeightHistory
from .utils import estimate_calories
from django.utils.timezone import now
from datetime import date, timedelta, datetime
from collections import OrderedDict
from django.contrib import messages


@login_required
def log_activity(request):
    # ─── PREAMBLE ───────────────────────────────────────────────────────────
    selected_date_str = request.GET.get("date")
    selected_date = date.today() if not selected_date_str else date.fromisoformat(selected_date_str)
    today = date.today()
    previous_date = selected_date - timedelta(days=1)
    next_date     = selected_date + timedelta(days=1)

    # ─── HANDLE FORM SUBMISSION ─────────────────────────────────────────────
    if request.method == "POST":
        form = ActivityLogForm(request.POST)
        if form.is_valid():
            new_log = form.save(commit=False)
            new_log.user = request.user
            new_log.logged_date = selected_date

            input_weight = form.cleaned_data.get('weight_kg')
            # Get the most recent history on or before selected_date
            weight_entry = WeightHistory.objects.filter(
                user=request.user,
                recorded_at__lte=selected_date
            ).order_by('-recorded_at').first()

            # ─── CHOOSE WEIGHT ───────────────────────────────────────────────
            if selected_date == today:
                # Today always uses current profile weight
                chosen_weight = request.user.weight
            else:
                # Past dates: manual input → history → profile
                if input_weight:
                    chosen_weight = input_weight
                elif weight_entry:
                    chosen_weight = weight_entry.weight_kg
                else:
                    chosen_weight = request.user.weight
            # ─── PERSIST HISTORY & ASSIGN ────────────────────────────────────
            WeightHistory.objects.update_or_create(
                user=request.user,
                recorded_at=selected_date,
                defaults={'weight_kg': chosen_weight}
            )
            new_log.weight_kg = chosen_weight
            # ─── ESTIMATE & SAVE ─────────────────────────────────────────────
            new_log.calories_burned = estimate_calories(
                activity_name=new_log.activity.name,
                duration_minutes=new_log.duration,
                user_weight_kg=new_log.weight_kg
            )
            new_log.save()
            messages.success(request, "Activity logged successfully.")
            return redirect(f"{reverse('log_activity')}?date={selected_date}#add-exercise")
        else:
            messages.error(request, "Please correct the errors in the form.")

    # ─── INITIAL FORM RENDER ────────────────────────────────────────────────
    else:
        form = ActivityLogForm(initial={"logged_date": selected_date})
        if selected_date != today:
            # Show weight field for past dates, pre-fill from history/profile
            weight_entry = WeightHistory.objects.filter(
                user=request.user,
                recorded_at__lte=selected_date
            ).order_by('-recorded_at').first()
            form.fields['weight_kg'].initial = (
                weight_entry.weight_kg if weight_entry else request.user.weight
            )
            form.fields['weight_kg'].label = (
                f"Weight on {selected_date.strftime('%d-%b-%Y')} (kg)"
            )
        else:
            # Remove the weight field entirely for today
            del form.fields['weight_kg']  # :contentReference[oaicite:1]{index=1}

    # ─── GATHER & RENDER ────────────────────────────────────────────────────
    logs_today = ActivityLog.objects.filter(
        user=request.user,
        logged_date=selected_date
    ).order_by("-created_at")
    # (…you can leave your “recent logs”, totals, etc. as before…)
    latest_ids = (
        ActivityLog.objects.filter(user=request.user)
        .values("activity")
        .annotate(latest_id=Max("id"))
        .values_list("latest_id", flat=True)
    )
    logs_recent = ActivityLog.objects.filter(id__in=latest_ids).order_by("-created_at")[:5]
    total_minutes = sum(log.duration for log in logs_today)
    total_calories = sum(log.calories_burned for log in logs_today)
    return render(request, "activity_log/log_activity.html", {
        "form": form,
        "logs_today": logs_today,
        "logs_recent": logs_recent,
        "selected_date": selected_date,
        "previous_date": previous_date,
        "next_date": next_date,
        "today": today,
        "total_minutes": total_minutes,
        "total_calories": total_calories,
        # include any other context (totals, recent logs) as before
    })

@login_required
def delete_activity_log(request, log_id): # ltr, for fe part need to refresh to the selected date instead of today
    try:
        log = get_object_or_404(ActivityLog, id=log_id, user=request.user)
        log.delete()
        messages.success(request, "Activity log deleted.")
    except Exception as e:
        messages.error(request, f"Failed to delete activity log: {str(e)}")
    return redirect('log_activity')

@login_required
def reuse_activity_log(request, log_id):
    try:
        # 1) Fetch the original log
        original_log = get_object_or_404(ActivityLog, id=log_id, user=request.user)

        # 2) Determine which date we're logging to
        selected_date_str = request.GET.get("date")
        target_date = date.today() if not selected_date_str else date.fromisoformat(selected_date_str)

        # 3) Choose the weight
        if target_date == date.today():
            # ─── Today: always use the latest profile weight ────────────
            chosen_weight = request.user.weight
        else:
            # ─── Past dates: lookup most recent history before or on that day ─
            weight_entry = (
                WeightHistory.objects
                .filter(user=request.user, recorded_at__lte=target_date)
                .order_by('-recorded_at')
                .first()
            )
            chosen_weight = weight_entry.weight_kg if weight_entry else request.user.weight

        # 4) Persist the weight in history (so your history table stays accurate)
        WeightHistory.objects.update_or_create(
            user=request.user,
            recorded_at=target_date,
            defaults={'weight_kg': chosen_weight}
        )

        # 5) Recalculate calories using the chosen weight
        calories = estimate_calories(
            activity_name=original_log.activity.name,
            duration_minutes=original_log.duration,
            user_weight_kg=chosen_weight
        )

        # 6) Create the new log entry
        ActivityLog.objects.create(
            user=request.user,
            activity=original_log.activity,
            duration=original_log.duration,
            weight_kg=chosen_weight,
            calories_burned=calories,
            logged_date=target_date,
        )

        messages.success(request, "Activity added successfully!")
    except Exception as e:
        messages.error(request, f"Failed to log activity: {e}")

    # Redirect back to the selected date view
    return redirect(f"{reverse('log_activity')}?date={target_date}")

@login_required
def calorie_report(request):
    try:
        days = int(request.GET.get("days", 7))
        if days not in [7, 30, 60]:
            raise ValueError("Invalid days value.")
    except ValueError:
        days = 7
        messages.warning(request, "Invalid range selected. Defaulted to the last 7 days.")

    today = date.today()
    start_date = today - timedelta(days=days - 1)

    try:
        logs = ActivityLog.objects.filter(
            user=request.user,
            logged_date__range=[start_date, today]
        ).order_by("logged_date")

        # Prepare daily totals
        daily_totals = OrderedDict()
        for i in range(days):
            d = start_date + timedelta(days=i)
            daily_totals[d.strftime("%d %b")] = 0

        for log in logs:
            label = log.logged_date.strftime("%d %b")
            daily_totals[label] += log.calories_burned

        labels = list(daily_totals.keys())
        values = list(daily_totals.values())

        # Preload weight entries for this user
        weight_entries = WeightHistory.objects.filter(
            user=request.user,
            recorded_at__lte=today
        ).order_by("recorded_at")

        # Track daily weights
        daily_weights = OrderedDict()
        latest_weight = request.user.weight  # fallback

        for label in labels:
            date_obj = datetime.strptime(label + f" {today.year}", "%d %b %Y").date()

            # Find latest weight before or on that day
            entry = next((w for w in reversed(weight_entries) if w.recorded_at <= date_obj), None)
            if entry:
                latest_weight = entry.weight_kg
            daily_weights[label] = latest_weight

        weight_values = list(daily_weights.values())

        return render(request, 'activity_log/calorie_report.html', {
            'labels': labels,
            'values': values,
            'days': days,
        })

    except Exception as e:
        messages.error(request, "Something went wrong while generating the report.")
        return render(request, 'activity_log/calorie_report.html', {
            'labels': [],
            'values': [],
            'days': days,
        })

@login_required
def download_calorie_report(request):
    if request.method == "POST":
        try:
            days = int(request.GET.get("days", 7))  # days=30 is in URL
            if days not in [7, 30, 60]:
                days = 7
        except (ValueError, TypeError):
            days = 7

        chart_image = request.POST.get("chart_image")
        today = date.today()
        start_date = today - timedelta(days=days - 1)

        activity_logs = ActivityLog.objects.filter(
            user=request.user,
            logged_date__range=[start_date, today]
        ).order_by("logged_date")

        total_minutes = sum(log.duration for log in activity_logs)
        total_calories = sum(log.calories_burned for log in activity_logs)

        template = get_template('activity_log/calorie_report_pdf.html')
        html = template.render({
            'user': request.user,
            'today': today,
            'days': days,
            'activity_logs': activity_logs,
            'total_minutes': total_minutes,
            'total_calories': total_calories,
            'chart_image': chart_image,
        })

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="calorie_report.pdf"'

        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Error generating PDF', status=500)
        return response

    return HttpResponse("Method not allowed", status=405)