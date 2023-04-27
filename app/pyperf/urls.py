from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from django.views.generic.base import RedirectView


urlpatterns = [
    path('', include('home.urls')),
    path('oauth/', include('oauth.urls')),
    path('admin/', admin.site.urls),
    path('flower/', RedirectView.as_view(url='/flower/'), name='flower'),
    path('redis/', RedirectView.as_view(url='/redis/'), name='redis'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path('debug/', include(debug_toolbar.urls))] + urlpatterns
