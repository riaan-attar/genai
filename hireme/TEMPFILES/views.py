
from django.shortcuts import render,redirect
from .forms import ApplicantSignUpForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.hashers import check_password

from .models import Applicant
def profile(request):
    return render(request, 'applicant/profile.html')

def jobs(request):
    return render(request, 'applicant/jobs.html')

def applogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            # Retrieve the applicant by username
            applicant = Applicant.objects.get(username=username)
            print(username)
            # Check if the password matches
            if check_password(password , applicant.password):
                request.session['applicant_id'] = applicant.id  # Store applicant ID in session
                return redirect('profile')  # Redirect to profile page or dashboard
            else:
                messages.error(request, 'Invalid password.')

        except Applicant.DoesNotExist:
            messages.error(request, 'Invalid username.')


    return render(request, 'applicant/login.html')



def appsignup(request):
    if request.method == "POST":
        form = ApplicantSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('applogin')
    else:
        form = ApplicantSignUpForm()
    return render(request, 'applicant/signup.html',{'form':form})


def interview(request):
    return render(request, 'applicant/interview.html')


import fitz
import os
import tempfile
import pathlib
import json
import google.ai.generativelanguage as glm
import google.generativeai as genai

def conv(pdf_path):
    doc = fitz.open(pdf_path)
    extracted_text = ""
    for page in doc:
        text = page.get_text()
        extracted_text += text
    doc.close()
    return extracted_text

def analyse(request):
    if request.method == 'POST':
        # Handle PDF upload
        pdf_docs = request.FILES.get('resume')
        
        if not pdf_docs:
            return render(request, 'applicant/analyse.html', {'response_text': 'No file uploaded.'})

        # Create a temporary file to store the PDF
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            for chunk in pdf_docs.chunks():
                temp_file.write(chunk)
            pdf_path = temp_file.name  # Corrected the variable name to 'pdf_path'

        # Extract text from the uploaded PDF
        text = conv(pdf_path)
        
        # Generative AI model call
        api_key = "AIzaSyDoke1EAtrezjMunJDw_Uv6dcyNRLltdUM"
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        response = model.generate_content(f"FROM THE {text} Analyse the resume and provide the feedback to the applicant in details explaining the areas of improvement as well as the strong points. or keywords that should be added in it.")
        
        # Extract response text
        out_text = ""
        # Assuming 'response._result.candidates[0].content.parts[0].text' contains the desired output text
        if response._result.candidates:
            out_text += response._result.candidates[0].content.parts[0].text
            
        # Print response to check
        print(out_text)

        return render(request, 'applicant/analyse.html', {'response_text': out_text})
    else:
        return render(request, 'applicant/analyse.html')
