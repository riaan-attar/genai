from django.shortcuts import render,redirect
from .forms import HRSignUpForm
from .models import hr 
from django.contrib.auth.hashers import check_password
import tempfile
import fitz
import os
import tempfile
import pathlib
import json
import google.ai.generativelanguage as glm
import google.generativeai as genai
 # Adjust the import path based on where conv is defined
# Create your views here.
def hrsignup(request):
    if request.method == "POST":
        form = HRSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('hrlogin')
    else:
        form = HRSignUpForm()
    return render(request, 'applicant/signup.html',{'form':form})

def hrlogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(1) 
        try:
            # Retrieve the applicant by username
            hrr = hr.objects.get(hr_name=username)
            print(2)
            #print(username)
            # Check if the password matches
            if check_password(password , hrr.password):
                print(3)
                request.session['hrr_id'] = hrr.id  # Store applicant ID in session
                return redirect('hr_index')  # Redirect to profile page or dashboard
            else:
                print(4)
                messages.error(request, 'Invalid password.')

        except hr.DoesNotExist:
            messages.error(request, 'Invalid username.')
            print(5)


    return render(request, 'applicant/login.html')

def index(request):
    return render(request, 'hr/index.html')

def short(request):
    return render(request, 'hr/short.html')

def manage(request):
    return render(request, 'hr/managejobs.html')

def quiz(request):
    return render(request, 'hr/quiz.html')

def conv(pdf_path):
    """
    Extracts text from the given PDF file path using PyMuPDF (fitz).
    """
    doc = fitz.open(pdf_path)
    extracted_text = ""
    for page in doc:
        extracted_text += page.get_text()
    doc.close()
    return extracted_text


def compare(request):
    if request.method == 'POST':
        pdf_doc1 = request.FILES.get('resume1')
        pdf_doc2 = request.FILES.get('resume2')

        if not pdf_doc1 or not pdf_doc2:
            return render(request, 'hr/compare.html', {
                'response_text1': 'No file uploaded for resume1.' if not pdf_doc1 else '',
                'response_text2': 'No file uploaded for resume2.' if not pdf_doc2 else ''
            })

        responses = []
        for pdf_doc in [pdf_doc1, pdf_doc2]:
            try:
                # Temporary file to store PDF
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    for chunk in pdf_doc.chunks():
                        temp_file.write(chunk)
                    pdf_path = temp_file.name

                # Extract text from the PDF
                text = conv(pdf_path)
                print("Extracted Text:", text)  # Debug log

                # Generative AI model
                api_key = "AIzaSyDoke1EAtrezjMunJDw_Uv6dcyNRLltdUM"
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-pro')

                response = model.generate_content(
                    f"Analyze the resume:\n{text}\nProvide feedback on strengths and areas of improvement."
                )
                print("AI Response:", response)  # Debug log

                # Extract text from the AI response
                out_text = ""
                if response._result.candidates:
                    out_text = response._result.candidates[0].content.parts[0].text
                responses.append(out_text)
            except Exception as e:
                responses.append(f"Error processing resume: {str(e)}")
            finally:
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)

        return render(request, 'hr/compare.html', {
            'response_text1': responses[0] if len(responses) > 0 else '',
            'response_text2': responses[1] if len(responses) > 1 else ''
        })

    return render(request, 'hr/compare.html')

