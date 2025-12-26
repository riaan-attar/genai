from django.shortcuts import render,redirect
from .forms import HRSignUpForm
from .models import hr,jd 
from applicant.models import JobApplication
from django.contrib.auth.hashers import check_password
from complogic import get_vec_job,get_vec_res
import fitz
import os
import tempfile
import pathlib
import json
import google.ai.generativelanguage as glm
import google.generativeai as genai
import markdown
from django.contrib import messages
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
load_dotenv()

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
        try:
            hrrs = hr.objects.filter(hr_name=username)
            if hrrs.exists():
                hrr = hrrs.first()
                if check_password(password, hrr.password):
                    request.session.flush()
                    request.session['hrr_id'] = hrr.id  # Store applicant ID in session
                    return redirect('hr_index')  # Redirect to profile page or dashboard
                else:
                    messages.error(request, 'Invalid password.')
            else:
                messages.error(request, 'Invalid username.')
        except hr.DoesNotExist:
            messages.error(request, 'Invalid username.')
    return render(request, 'applicant/login.html')

def hr_index(request):
    return render(request, 'hr/index.html')

def batch(request):
    results = []
    if request.method == "POST":
        job_title = request.POST.get("job_title") 
        job_desc_text = request.POST.get("job_desc")
        resumes = request.FILES.getlist('resumes')
        if not resumes:
            messages.error(request, 'No resumes uploaded.')
            return redirect('batch_upload_resumes')
        js = get_vec_job(job_desc_text)
        for resume_file in resumes:
            try:
                score_value = cosine_similarity([get_vec_res(resume_file)], [js])[0][0] * 100.0
                results.append({'resume_name': resume_file.name, 'score': score_value})
            except Exception as e:
                messages.error(request, f"Error processing resume: {str(e)}")
                continue
        results = sorted(results, key=lambda x: x['score'], reverse=True)
        return render(request, 'hr/batch.html', {'results': results})
    return render(request, 'hr/batch.html', {'results': results})

def short(request):
    Candidates = []
    if request.method == "POST":
        title = request.POST.get("job_title")
        number = int(request.POST.get("top_applicants"))
        score = float(request.POST.get("score"))
        # Filter candidates
        Candidates = JobApplication.objects.filter(job__title=title, score__gte=score).order_by('-score')
        # Add score_percentage to each candidate
        for candidate in Candidates:
            candidate.score_percentage = candidate.score * 10
    jobs = jd.objects.all()
    return render(request, 'hr/short.html', {'jobs': jobs, 'Candidates': Candidates})

def manage(request):
    if request.method == "POST":
        # Handle Delete Request
        delete_job_id = request.POST.get("delete_job_id")
        if delete_job_id:
            try:
                job_to_delete = jd.objects.get(id=delete_job_id)
                job_to_delete.delete()
                messages.success(request, 'Job deleted successfully.')
            except jd.DoesNotExist:
                messages.error(request, 'Job not found.')
            return redirect('manage')

        # Handle Add Job Request
        job_title = request.POST.get("jobName")
        job_desc = request.POST.get("jobDesc")
        idx = request.session.get("hrr_id")
        try:
            hrr = hr.objects.get(id=idx)
        except hr.DoesNotExist:
            messages.error(request, 'HR not found.')
            return redirect('manage')
        
        info = jd.objects.create(hr=hrr, title=job_title, description=job_desc)
        info.save()
        skills_vector = get_vec_job(job_desc)
        info.save_vector(skills_vector)
        messages.success(request, 'Job added successfully.')
        return redirect('manage')

    # Retrieve all jobs
    jobs = jd.objects.all()
    return render(request, 'hr/managejobs.html', {'jobs': jobs})

def quiz(request):
    return render(request, 'hr/quiz.html')

def conv(pdf_path):
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
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    for chunk in pdf_doc.chunks():
                        temp_file.write(chunk)
                    pdf_path = temp_file.name
                text = conv(pdf_path)
                api_key = os.getenv("GOOGLE_API_KEY")
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-pro')

                response = model.generate_content(
                    f"Analyze the resume:\n{text}\nProvide feedback on strengths and areas of improvement."
                )
                out_text = ""
                if response._result.candidates:
                    out_text = response._result.candidates[0].content.parts[0].text
                html_response = markdown.markdown(out_text)
                responses.append(html_response)
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

def logout(request):
    request.session.flush()
    return redirect('applogin')
