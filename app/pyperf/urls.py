from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    path('', include('home.urls')),
    path('oauth/', include('oauth.urls')),
    path('admin/', admin.site.urls),
    path('flower/', RedirectView.as_view(url='/flower/'), name='flower'),
    path('redis/', RedirectView.as_view(url='/redis/'), name='redis'),
    path('flush-cache/', views.flush_cache_view, name='flush_cache'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler400 = 'myapp.views.handler400_view'
handler403 = 'myapp.views.handler403_view'
handler404 = 'myapp.views.handler404_view'
handler500 = 'myapp.views.handler500_view'


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path('debug/', include(debug_toolbar.urls))] + urlpatterns
