#from django.conf.urls import include, url
from django.conf.urls import url
#from . import views
#from raspirover import views
from django.contrib import admin
from raspirover import views as raspirover_views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import logout


urlpatterns = [
#        url(r'^admin/', include(admin.site.urls)),    
	url(r'^admin/', admin.site.urls),
	url(r'^$', raspirover_views.index, name='index'),
	url(r'sobre_mi/$', raspirover_views.sobre_mi, name='sobre_mi'), 
	url(r'gracias/(?P<username>[\w]+)/(?P<login>[\w]+)/$', raspirover_views.gracias, name='gracias'),
	url(r'registro/$', raspirover_views.registro, name='registro'),
	url(r'login/$', raspirover_views.login, name='login'),
	url(r'editar_contrasena/$', raspirover_views.editar_contrasena, name='editar_contrasena'),
	url(r'editar_foto/$', raspirover_views.editar_foto, name='editar_foto'),
        url(r'^logout/$', auth_views.logout, name='logout'),
	url(r'eliminar_usuario/$', raspirover_views.eliminar_usuario, name='eliminar_usuario'), 
#	url(r'logout/$', 'django.contrib.auth.views.logout', {'next_page': 'index'} ),
	url(r'explorar/$', raspirover_views.explorar, name='explorar'),
	url(r'analizar/$', raspirover_views.analizar, name='analizar'), 	 
	url(r'manual/$', raspirover_views.manual, name='manual'), 	   
	url(r'auto/$', raspirover_views.auto, name='auto'), 
	url(r'salir/$', raspirover_views.salir, name='salir'), 	
	url(r'apagar/$', raspirover_views.apagar, name='apagar'), 	
	url(r'reboot/$', raspirover_views.reboot, name='reboot'), 	
	url(r'mostrardatos/$', raspirover_views.mostrardatos, name='mostrardatos'),
	url(r'mostrarvoltaje/$', raspirover_views.mostrarvoltaje, name='mostrarvoltaje'),
	url(r'^detallesExploracion/(?P<id_exploracion>\d+)', raspirover_views.detallesExploracion, name='detallesExploracion'),
	url(r'^eliminarExploracion/(?P<id_exploracion>\d+)', raspirover_views.eliminarExploracion, name='eliminarExploracion'),
	url(r'^mostrarGrafica/(?P<id_exploracion>\d+)/(?P<sensor_tipo>[\w]+)', raspirover_views.mostrarGrafica, name='mostrarGrafica'),	
	url(r'^mostrarMapa/(?P<id_exploracion>\d+)', raspirover_views.mostrarMapa, name='mostrarMapa'),	
]
