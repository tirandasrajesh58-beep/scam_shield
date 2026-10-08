from django.urls import path
from . import views

app_name = 'impersonation'

urlpatterns = [
    path('', views.analyze, name='analyze'),
]
