from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls,name='admin'),
    path('',include('shopping.urls')),
    path('dashboard/',  include('dashboard.urls')),
    path('api/',include('api.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('oauth/', include('social_django.urls', namespace='social')), 
    path('accounts/', include('allauth.urls')),
  #  path('',include('user.urls')),
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)