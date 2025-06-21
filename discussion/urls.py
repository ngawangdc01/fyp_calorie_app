from django.urls import path
from . import views

urlpatterns = [
    path('', views.discussion_list, name='discussion_list'),  # Explore
    path('your_post/', views.your_posts, name='your_posts'),       # Your Posts

    path('create/', views.create_discussion, name='create_discussion'),
    path('<int:pk>/', views.discussion_detail, name='discussion_detail'),
    path('<int:pk>/edit/', views.edit_discussion, name='edit_discussion'),
    path('<int:pk>/delete/', views.delete_discussion, name='delete_discussion'),

    path('reply/<int:pk>/edit/', views.edit_reply, name='edit_reply'),
    path('reply/<int:pk>/delete/', views.delete_reply, name='delete_reply'),
]