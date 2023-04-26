from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.home_view, name='index'),
    path('save/', views.save_iperf, name='iperf'),
    path('<int:pk>/', views.result_view, name='result'),
    path('<int:pk>.png', views.image_view, name='image'),
    path('<int:pk>/graph/', views.graph_view, name='graph'),
    path('<int:pk>/map/', views.map_view, name='map'),
    path('ajax/tdata/', views.tdata_view_a, name='ajax_tdata'),
    path('ajax/graph/', views.graph_view_a, name='ajax_graph'),
    path('ajax/map/', views.map_view_a, name='ajax_map'),
]
