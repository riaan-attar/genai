from django import forms
from .models import hr, jd
from django.contrib.auth.hashers import make_password
class HRSignUpForm(forms.ModelForm):
    #password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = hr
        fields = ['hr_name', 'company_name', 'email', 'password']

        widgets = {
            'hr_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'HR Name', 
                'aria-label': 'HR Name'
            }),
            'company_name': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Company Name',
                'aria-label': 'Company Name'           
            }),
            'email': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Email', 
                'aria-label': 'Email'
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Password', 
                'aria-label': 'Password'
            }),
        }
    def save(self, commit=True):
        hr = super().save(commit=False)
        if hr.password:
            hr.password = make_password(hr.password)
        if commit:
            hr.save()
        return hr


class JDForm(forms.ModelForm):
    class Meta:
        model = jd
        fields = ['title', 'description']

