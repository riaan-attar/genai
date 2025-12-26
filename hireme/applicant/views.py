
from django.shortcuts import render,redirect
from .forms import ApplicantSignUpForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from .models import Applicant,Resume,JobApplication
from hr.models import hr,jd
from complogic import get_vec_res, get_vec_job
import fitz
import os
import tempfile
import pathlib
import json
import google.ai.generativelanguage as glm
import google.generativeai as genai
from sklearn.metrics.pairwise import cosine_similarity
import markdown
from dotenv import load_dotenv
load_dotenv()

def landing(request):
    return render(request,'landing.html')

def profile(request):
    applicant_id = request.session.get('applicant_id')
    if not applicant_id:
        messages.error(request, 'Please log in to access your profile.')
        return redirect('applogin')
    try:
        applicant = Applicant.objects.get(id=applicant_id)
    except Applicant.DoesNotExist:
        messages.error(request, 'Applicant not found.')
        return redirect('applogin')
    '''if request.method == 'POST':
        applicant.username = request.POST.get('username', applicant.username)
        applicant.email = request.POST.get('email', applicant.email)
        applicant.phone_number = request.POST.get('phone_number', applicant.phone_number)
        password = request.POST.get('password')
        if password:
            applicant.password = make_password(password)
        applicant.linkedin = request.POST.get('linkedin', applicant.linkedin)
        applicant.github = request.POST.get('github', applicant.github)
        soft_score = request.POST.get('soft_score')
        if soft_score:
            try:
                applicant.soft_score = int(soft_score)
            except ValueError:
                messages.error(request, 'Invalid soft score. Please enter a valid number.')
                return redirect('profile')
        applicant.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')'''
    return render(request, 'applicant/profile.html', {'applicant': applicant})

def jobs(request):
    if request.method == "POST":
        applicant_id = request.session.get("applicant_id")
        job_id = request.POST.get('job_id')
        if applicant_id:
            try:
                job = jd.objects.get(id=job_id)
                applicant = Applicant.objects.get(id = applicant_id)
                resume = Resume.objects.filter(uploaded_by = applicant).first() 
                vcand = resume.get_vector()
                vjd = job.get_vector()
                score = cosine_similarity([vcand], [vjd])
                score = score*10.0
                if JobApplication.objects.filter(applicant = applicant):
                    messages.error(request,"already applied for this job")
                else:
                    JobApplication.objects.create(applicant=applicant, job=job, score=score)
                    messages.success(request, 'Successfully applied for the job!')
            except (jd.DoesNotExist, Applicant.DoesNotExist):
                messages.error(request, 'Job or Applicant not found.')
        else:
            messages.error(request, 'You need to log in to apply for jobs.')
    jobs = jd.objects.all()
    return render(request, 'applicant/jobs.html',{'jobs':jobs})

def applogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            # Retrieve the applicant by username
            applicant = Applicant.objects.get(username=username)
            # Check if the password matches
            if check_password(password , applicant.password):
                request.session.flush()
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

def resume_upload(request):
    try:
        applicant_id = request.session.get('applicant_id')
        applicant = Applicant.objects.get(id = applicant_id)
        resume = Resume.objects.filter(uploaded_by = applicant).first()
    except Resume.DoesNotExist:
        resume = None
    if request.method == "POST":
        resume_file = request.FILES.get('resume_file')
        applicant.username = request.POST.get('username', applicant.username)
        applicant.email = request.POST.get('email', applicant.email)
        applicant.phone_number = request.POST.get('number', applicant.phone_number)
        password = request.POST.get('password')
        if password:
            applicant.password = make_password(password)
        applicant.linkedin = request.POST.get('linkedin', applicant.linkedin)
        applicant.github = request.POST.get('github', applicant.github)
        applicant.save() 
        soft_score = request.POST.get('soft_score')
        if soft_score:
            try:
                applicant.soft_score = int(soft_score)
            except ValueError:
                messages.error(request, 'Invalid soft score. Please enter a valid number.')
        applicant.save()
        if resume_file:
            if not resume_file.name.endswith(".pdf"):
                messages.error(request,'Only pdfs allowed')
                return redirect('profile')

            if resume:
                resume.resume_file = resume_file
                resume.is_batch_upload =False
                resume.save()
                skills_vec = get_vec_res(resume.resume_file.path)
                resume.save_vector(skills_vec)
                applicant.save()
                
            else:
                new_resume = Resume(uploaded_by=applicant, resume_file=resume_file, is_batch_upload=False)
                new_resume.save()
                skills_vec = get_vec_res(resume.resume_file.path)
                new_resume.save_vector(skills_vec)
                applicant.resume = new_resume
                applicant.save()
            messages.success(request, 'Resume uploaded successfully!')
            return redirect('profile')  # Redirect to the profile page after successful upload
        else:
            messages.error(request, 'Please choose a file to upload.')

    return redirect('profile')

def interview(request):
    if request.method == 'POST':
        # Retrieve answers from the form (using get instead of getlist for single values)
        answers1 = request.POST.get('answers1')  # Get the first answer
        answers2 = request.POST.get('answers2')  # Get the second answer
        answers3 = request.POST.get('answers3')  # Get the third answer
        
        # Predefined questions
        question1 = "Can you describe a time when you had to explain a complex idea to someone who had little to no understanding of the subject? How did you ensure they understood?"
        question2 = "Tell me about a time when you faced a significant challenge at work. How did you approach solving it, and what was the outcome?"
        question3 = "Describe a situation where you worked on a team project. How did you contribute to the team’s success, and how did you handle conflicts or disagreements within the team?"
        # Configure API key and initialize the model
        api_key = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Generate content with the answers and questions
        response = model.generate_content(f"Here is the answer: '{answers1}' to the question: '{question1}', followed by answer: '{answers2}' to the question: '{question2}', and answer: '{answers3}' to the question: '{question3}'. Act like a soft skills interviewer and give a score based on the answers. The score should be out of 10 and floating-point scores are acceptable. you dont have to give score for 3 diffrenet answers only one score that you think is best for the applicant.just give answer score float number no else text")
        # Extract response text and the score
        out_text = ""
        score = None
        if response._result.candidates:
            out_text += response._result.candidates[0].content.parts[0].text
            # Try to extract the score (assuming the score is in the response text)
            if "score" in out_text.lower():
                try:
                    # Looking for the score after the word "score"
                    score = float(out_text.split("score")[1].split()[0])
                except (ValueError, IndexError):
                    score = None  # If we can't parse the score, set it to None
        score = float(out_text)
        applicant_id = request.session.get('applicant_id')
        applicant = Applicant.objects.get(id=applicant_id)
        applicant.soft_score = score
        applicant.save()
        # If no score is extracted, handle the error case
        return redirect('profile')  # Redirect to the profile page or another page
    # If not POST, render the interview form
    return render(request, 'applicant/interview.html')

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
        text = conv(pdf_path)
        api_key = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')        
        response = model.generate_content(f"FROM THE {text} Analyse the resume and provide the feedback to the applicant in details explaining the areas of improvement as well as the strong points. or keywords that should be added in it.")
        out_text = ""
        # Assuming 'response._result.candidates[0].content.parts[0].text' contains the desired output text
        if response._result.candidates:
            out_text += response._result.candidates[0].content.parts[0].text
        html_ip = markdown.markdown(out_text)
        return render(request, 'applicant/analyse.html', {'response_text': html_ip})
    else:
        return render(request, 'applicant/analyse.html')

def appquiz(request):
    return render(request,'applicant/appquiz.html')
    
def logout(request):
    request.session.flush()
    return redirect('applogin')
