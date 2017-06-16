# -*- encoding: utf-8 -*- 
from django.forms import ModelForm, Textarea, TextInput, PasswordInput, NumberInput, EmailInput
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password
from .models import *
from django.utils.safestring import mark_safe
from django.core.validators import MaxValueValidator

#Formulario para registro de los usuarios
class UsuarioForm(ModelForm):
	
	#Campo para poder confirmar la contraseña introducida
	password1 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)
	photo = forms.ImageField(required=False)

	#Se sobreescribe el formulario para poder modificar las propiedades de los campos
	def __init__(self, *args, **kwargs):

		super(UsuarioForm, self).__init__(*args, **kwargs)
		#Se hacen obligatorios los campos de email, nombre y apellido
		self.fields['email'].required = True
		self.fields['username'].widget.attrs['placeholder'] = "Nombre"
		self.fields['email'].widget.attrs['placeholder'] = "Email"
		self.fields['password'].widget.attrs['placeholder'] = "Contraseña"
		self.fields['password1'].widget.attrs['placeholder'] = "Confirmar contraseña"
		self.fields['photo']
	
	class Meta:
		model = Usuario
		fields = ['username', 'email', 'password']

		#Se cambia el tipo de caja HTML del atributo password para que salgan asteriscos al introducirla. Por defecto sale texto normal
		widgets = {
			'password': PasswordInput,
		}		
	
		#Se personalizan los mensajes de error
		error_messages = {
			'username': {
				'required': ("El nickname es obligatorio"),
				'invalid': ("Nickname inválido"),
			},
			'email': {
				'required': ("El email es obligatorio"),
				'invalid': ("Email inválido"),
			},
			'password': {
				'required': ("La contraseña es obligatoria"),
			},
		}
		
		#Se personalizan las etiquetas de aquellos atributos donde la etiqueta por defecto no era buena
		labels={
			'username': ("Nombre"),
			'email': ("Email"),
			'photo': ("Foto de Perfil")
		}
	
	#VALIDACIONES
	def clean_password1(self):
		#Comprobar que la confirmacion de la contraseña coincide
		password = self.cleaned_data.get("password")
		password1 = self.cleaned_data.get("password1")
		if password and password1 and password != password1:
			raise forms.ValidationError("La contraseña no coincide")
		return password1	
			
	#El username no puede contener un @
	def clean_username(self):
		username = self.cleaned_data['username']
		if '@' in username:
			raise forms.ValidationError('No puede contener @')
		return username	
	
	
	def save(self, commit=True):	
		user = super(UsuarioForm, self).save(commit=False)
				
		#Para guardar la contraseña en formato hash
		user.set_password(self.cleaned_data["password"])	
		if commit:
			user.save()
		return user	

class RegistroUserForm(forms.Form):
 
	username = forms.CharField(min_length=4,widget=forms.TextInput(attrs={'class': 'form-control'}))
	email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
	password = forms.CharField(min_length=4,widget=forms.PasswordInput(attrs={'class': 'form-control'}))
	repetir_password = forms.CharField(min_length=4,widget=forms.PasswordInput(attrs={'class': 'form-control'}))
	photo = forms.ImageField(required=False)
 
	def clean_username(self):
		"""Comprueba que no exista un username igual en la db"""
		username = self.cleaned_data['username']
		if User.objects.filter(username=username):
			raise forms.ValidationError('username de usuario ya registrado.')
		return username
 
	def clean_email(self):
		"""Comprueba que no exista un email igual en la db"""
		email = self.cleaned_data['email']
		if User.objects.filter(email=email):
			raise forms.ValidationError('Ya existe un email igual en la db.')
		return email
 
	def clean_password2(self):
		"""Comprueba que password y repetir_password sean iguales."""
		password = self.cleaned_data['password']
		repetir_password = self.cleaned_data['repetir_password']
		if password != repetir_password:
			raise forms.ValidationError('Las contrasenas no coinciden.')
		return repetir_password

#editar email
class EditarContrasenaForm(forms.Form):
 
	actual_password = forms.CharField(
		label='Contraseña actual',
		min_length=4,
		widget=forms.PasswordInput(attrs={'class': 'form-control'}))
 
	password = forms.CharField(
		label='Nueva contraseña',
		min_length=4,
		widget=forms.PasswordInput(attrs={'class': 'form-control'}))
 
	repetirpassword = forms.CharField(
		label='Repetir contraseña',
		min_length=4,
		widget=forms.PasswordInput(attrs={'class': 'form-control'}))
 
	def clean_password2(self):
		"""Comprueba que password y repetir_password sean iguales."""
		password = self.cleaned_data['password']
		repetir_password = self.cleaned_data['repetir_password']
		if password != repetir_password:
			raise forms.ValidationError('Las contraseñas no coinciden.')
		return repetir_password
 
#editar foto
class EditarFotoForm(forms.Form):
	imagen = forms.ImageField(required=False)


class HorizRadioRenderer(forms.RadioSelect.renderer):
    """ this overridcheckbox_1es widget method to put radio buttons horizontally
        instead of vertically.
    """
    def render(self):
            """Outputs radios"""
            return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))

#Formulario de exploracion
class ExploracionForm(forms.Form):

	nombre = forms.CharField(label='Título de exploración', required=False, min_length=2, max_length=50)
	descripcion = forms.CharField(label='Descripción', required=False, max_length=140)
	tiempo = forms.DecimalField(label='Tiempo de disparo de la BBDD (segundos)',required=False)
	temperatura = forms.BooleanField(label='',required=False, widget=forms.CheckboxInput(attrs={'class': 'hide-checkbox'}))
	humedad = forms.BooleanField(label='',required=False, widget=forms.CheckboxInput(attrs={'class': 'hide-checkbox'}))
	gas = forms.BooleanField(label='',required=False, widget=forms.CheckboxInput(attrs={'class': 'hide-checkbox'}))
	luz = forms.BooleanField(label='',required=False, widget=forms.CheckboxInput(attrs={'class': 'hide-checkbox'}))
	camara = forms.BooleanField(label='',required=False, widget=forms.CheckboxInput(attrs={'class': 'hide-checkbox'}))

	class Meta:
		model = Sensores

	#def __init__(self, *args, **kwargs):
	#	super(ExploracionForm, self).__init__(*args, **kwargs)

	#	for field in self.fields:
	#		self.fields[field].error_messages = {'required': 'Nombre de la exploración es obligatorio'}

		
	#	#Se personalizan los mensajes de error
	#	error_messages = {
	#		'nombre': {
	#			'required': ("El nombre de la exploración es obligatorio"),
	#		},
	#	}
