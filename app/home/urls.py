from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.home_view, name='index'),
    path('save/', views.save_iperf, name='iperf'),
    path('data/<int:pk>/', views.result_view, name='result'),
]
