from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.home_view, name='index'),
    path('speedtest/', views.speedtest_view, name='speedtest'),
    path('save/', views.save_iperf, name='iperf'),
    path('<int:pk>/', views.result_view, name='result'),
    path('<int:pk>.png', views.image_view, name='image'),
    path('<int:pk>/graph/', views.graph_view, name='graph'),
    path('<int:pk>/map/', views.map_view, name='map'),
    path('ajax/tdata/<int:pk>/', views.tdata_view_a),
    path('ajax/graph/<int:pk>/', views.graph_view_a),
    path('ajax/map/<int:pk>/', views.map_view_a),
    path('ajax/delete/hook/<int:pk>/', views.del_hook_view_a),
    # path('ajax/delete/result/<int:pk>/', views.del_result_view_a),
]
