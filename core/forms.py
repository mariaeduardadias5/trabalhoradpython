from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Senha", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmação da senha", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'email']  # só nome e email
        labels = {
            'first_name': 'Nome completo',
            'email': 'E-mail',
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("As senhas não coincidem.")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # usar email como username
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user