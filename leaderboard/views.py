from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt  # only if using pure JS fetch()
from django.db.models import Sum
from django.http import JsonResponse
from datetime import date, timedelta
from activity_log.models import ActivityLog
from user_management.models import User

@login_required
def leaderboard_view(request):
    days = int(request.GET.get('days', 7))
    if days not in [7, 30, 60]:
        days = 7

    today = date.today()
    start_date = today - timedelta(days=days - 1)

    # Aggregate total calories for each user
    user_totals = (
        ActivityLog.objects
        .filter(
            logged_date__range=[start_date, today],
            user__is_visible_in_leaderboard=True
        )
        .values('user_id', 'user__username')
        .annotate(total_calories=Sum('calories_burned'))
        .order_by('-total_calories')[:50]
    )

    return render(request, 'leaderboard/leaderboard.html', {
        'user_totals': user_totals,
        'days': days,
    })

@login_required
@require_POST
def toggle_leaderboard_visibility(request):
    is_visible = request.POST.get("is_visible") == "true"
    user = request.user
    user.is_visible_in_leaderboard = is_visible
    user.save(update_fields=["is_visible_in_leaderboard"])
    return JsonResponse({"success": True, "is_visible": user.is_visible_in_leaderboard})