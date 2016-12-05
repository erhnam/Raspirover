from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView
from raspirover import views
import debug_toolbar
  
admin.autodiscover()

urlpatterns = [
    url(r'^', include('raspirover.urls')),
    url(r'^admin/', include(admin.site.urls)),    
    url (r'^login', views.login, name='login'),
    url (r'^logout', views.logout, name='logout'),
    url(r'^__debug__/', include(debug_toolbar.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
