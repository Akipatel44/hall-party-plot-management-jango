from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from hall_app import views
from hall_app.views import admin_dashboard

from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('hall_app.urls')),
    path('logout/', views.custom_logout, name='logout'),
    path('accounts/profile/', RedirectView.as_view(pattern_name='profile', permanent=False)),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)