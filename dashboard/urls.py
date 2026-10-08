from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashboard/', views.home, name='home'),
    path('history/', views.history, name='history'),
    path('record/<int:pk>/', views.record_detail, name='record_detail'),
    path('record/<int:pk>/delete/', views.record_delete, name='record_delete'),
]
