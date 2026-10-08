from django.urls import path
from . import views

app_name = 'app_analysis'

urlpatterns = [
    path('', views.analyze, name='analyze'),
]
