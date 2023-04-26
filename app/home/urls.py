from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.home_view, name='index'),
    path('save/', views.save_iperf, name='iperf'),
    path('<int:pk>/', views.result_view, name='result'),
    path('<int:pk>.png', views.image_view, name='image'),
    path('<int:pk>/graph/', views.graph_view, name='graph'),
    path('ajax/tdata/', views.tdata_view, name='tdata'),
]
