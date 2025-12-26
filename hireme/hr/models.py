from django.db import models
import pickle
# Create your models here.
class hr(models.Model):
    hr_name = models.CharField(max_length = 150)
    company_name = models.CharField(max_length=150)
    email = models.EmailField(unique = True)
    password = models.CharField(max_length = 150)
    def __str__(self):
        return f"{self.hr_name} ({self.company_name})"

class jd(models.Model):
    hr = models.ForeignKey(hr,on_delete=models.CASCADE,related_name = 'jobdesc')
    title = models.CharField(max_length=150)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)
    skills_vector = models.BinaryField(null = True, blank = True)
    def save_vector(self,vector):
        self.skills_vector = pickle.dumps(vector)
        self.save()

    def get_vector(self):
        return pickle.loads(self.skills_vector) if self.skills_vector else None

    def __str__(self):
        return f"{self.title} ({self.hr.company_name})"

