from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Usuario, Rol


class LoginForm(AuthenticationForm):
    """Formulario personalizado de login"""
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario o Email',
        })
    )
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
        })
    )
    
    class Meta:
        model = Usuario
        fields = ('username', 'password')


class RegistroForm(UserCreationForm):
    """Formulario personalizado de registro"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com',
        })
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre',
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu apellido',
        })
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        help_text='Elige un nombre de usuario único (letras, números, - y _ permitidos)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'nombre_usuario',
            'autocomplete': 'username',
        })
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres',
            'autocomplete': 'new-password',
        })
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirma tu contraseña',
            'autocomplete': 'new-password',
        })
    )
    rol = forms.ModelChoiceField(
        queryset=Rol.objects.filter(nombre__in=['usuario', 'organizador']),
        required=True,
        widget=forms.RadioSelect(),
        label='Tipo de Cuenta',
        empty_label=None
    )
    
    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'email', 'username', 'rol', 'password1', 'password2')
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso. Elige otro.')
        
        # Validar caracteres permitidos
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise forms.ValidationError('El nombre de usuario solo puede contener letras, números, guiones y guiones bajos.')
        
        # Validar longitud mínima
        if len(username) < 3:
            raise forms.ValidationError('El nombre de usuario debe tener al menos 3 caracteres.')
        
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return email
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1 and len(password1) < 8:
            raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres.')
        return password1
    
    def save(self, commit=True):
        user = super().save(commit=False)
        rol = self.cleaned_data.get('rol')
        user.rol = rol
        if commit:
            user.save()
        return user
