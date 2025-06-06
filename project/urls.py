from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('', include('matchmaking.urls')),
    path('select2/', include('django_select2.urls')),
    path('firebase-messaging-sw.js', TemplateView.as_view(template_name="firebase-messaging-sw.js", content_type='application/javascript')),
]
    
if settings.DEBUG:  # Only for development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    

from django.conf.urls import handler404
from users.views import custom_404_view
handler404 = custom_404_view

