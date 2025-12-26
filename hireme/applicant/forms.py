from django import forms
from .models import Applicant, Resume
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import AuthenticationForm
class ApplicantSignUpForm(forms.ModelForm):
    #password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Applicant
        fields = ['username', 'email', 'phone_number', 'password']

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Username', 
                'aria-label': 'username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'email', 
                'aria-label': 'email'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'phone_number', 
                'aria-label': 'phone_number'
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Password', 
                'aria-label': 'Password'
            }),
        }

    def save(self, commit=True):
        applicant = super().save(commit=False)
        if applicant.password:
            applicant.password = make_password(applicant.password)
        if commit:
            applicant.save()
        return applicant

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['resume_file']


    def save(self, commit=True):
        applicant = super().save(commit=False)
        applicant.password = applicant.password
        if commit:
            applicant.save()
        return applicant



