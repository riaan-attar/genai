from django.db import models
import pickle
from hr.models import jd
# Create your models here.
class Applicant(models.Model):
    username = models.CharField(max_length=150,unique = True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length = 15)
    password = models.CharField(max_length= 200)
    linkedin = models.CharField(max_length= 200)
    github = models.CharField(max_length= 200)
    resume = models.OneToOneField('Resume', on_delete=models.SET_NULL, null=True, blank=True)
    soft_score = models.FloatField(null=True, blank=True)
    def __str__(self):
        return self.username

class Resume(models.Model):
    uploaded_by = models.ForeignKey(Applicant, on_delete=models.CASCADE, null=True, blank=True, related_name='resumes')
    is_batch_upload = models.BooleanField(default=False)
    resume_file = models.FileField(upload_to ='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add = True)
    resume_vector = models.BinaryField(null = True, blank = True)
    
    def save_vector(self,vector):
        self.resume_vector = pickle.dumps(vector)
        self.save()
    def get_vector(self):
        return pickle.loads(self.resume_vector) if self.resume_vector else None
    def __str__(self):
        return f"Resume of {self.uploaded_by.username} uploaded on {self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}"

class JobApplication(models.Model):  # Subclass for Applications
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(jd, on_delete=models.CASCADE, related_name='applications')
    score = models.FloatField()
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.applicant.username} applied to {self.job.title} (Score: {self.score})"
