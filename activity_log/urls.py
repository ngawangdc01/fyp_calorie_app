from django.urls import path
from . import views

urlpatterns = [
    path('log/', views.log_activity, name='log_activity'),
    path('log/delete/<int:log_id>/', views.delete_activity_log, name='delete_activity_log'),
    path('log/reuse/<int:log_id>/', views.reuse_activity_log, name='reuse_activity_log'),
    path('report/', views.calorie_report, name='calorie_report'),
    path('report/download/', views.download_calorie_report, name='download_calorie_report'),
]
