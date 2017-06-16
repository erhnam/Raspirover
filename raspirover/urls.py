from django.conf.urls import include, url
from . import views
from raspirover import views
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),    
	url(r'^$', views.index, name='index'),
	url(r'sobre_mi/$', views.sobre_mi, name='sobre_mi'), 
	url(r'gracias/(?P<username>[\w]+)/(?P<login>[\w]+)/$',views.gracias, name='gracias'),
	url(r'registro/$', views.registro, name='registro'),
	url(r'login/$', views.login, name='login'),
	url(r'editar_contrasena/$', views.editar_contrasena, name='editar_contrasena'),
	url(r'editar_foto/$', views.editar_foto, name='editar_foto'),
	url(r'eliminar_usuario/$', views.eliminar_usuario, name='eliminar_usuario'), 
	url(r'logout/$', 'django.contrib.auth.views.logout', {'next_page': 'index'} ),
	url(r'explorar/$', views.explorar, name='explorar'),
	url(r'analizar/$', views.analizar, name='analizar'), 	 
	url(r'manual/$', views.manual, name='manual'), 	   
	url(r'auto/$', views.auto, name='auto'), 
	url(r'salir/$', views.salir, name='salir'), 	
	url(r'apagar/$', views.apagar, name='apagar'), 	
	url(r'reboot/$', views.reboot, name='reboot'), 	
	url(r'mostrardatos/$', views.mostrardatos, name='mostrardatos'),
	url (r'^detallesExploracion/(?P<id_exploracion>\d+)', views.detallesExploracion, name='detallesExploracion'),
	url (r'^eliminarExploracion/(?P<id_exploracion>\d+)', views.eliminarExploracion, name='eliminarExploracion'),
	url (r'^mostrarGrafica/(?P<id_exploracion>\d+)/(?P<sensor_tipo>[\w]+)', views.mostrarGrafica, name='mostrarGrafica'),	
]
