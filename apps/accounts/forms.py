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
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico (opcional)',
        })
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre',
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido',
        })
    )
    rol = forms.ModelChoiceField(
        queryset=Rol.objects.filter(nombre__in=['usuario', 'organizador']),
        required=True,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
        }),
        label='Tipo de cuenta',
        empty_label=None
    )
    
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'first_name', 'last_name', 'rol', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Usuario',
            })
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        rol = self.cleaned_data.get('rol')
        user.rol = rol
        if commit:
            user.save()
        return user
