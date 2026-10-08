from django.urls import path
from . import views

app_name = 'risk_detection'

urlpatterns = [
    path('profile/', views.profile_analyze, name='profile_analyze'),
    path('message/', views.message_analyze, name='message_analyze'),
]
