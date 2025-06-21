"""
URL configuration for fyp_calorie_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

# Redirect root URL to login page in 'user_management' app
def redirect_to_login(request):
    return redirect('login')

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', redirect_to_login, name='home'),  # Redirect root URL to login
    path('user/', include('user_management.urls')),
    path('activity/', include('activity_log.urls')),
    path('discussions/', include('discussion.urls')),
    path('leaderboard/', include('leaderboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)