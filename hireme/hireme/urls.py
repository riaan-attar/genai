"""
URL configuration for hireme project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from hr.views import *
from applicant.views import *
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing,name="landing"),
    path('hrindex/', hr_index,name="hr_index"),
    path('short/', short),
    path('hrindex/',hr_index,name="hr_index"),
    path('short/', short,name="short"),
    path('profile/', profile,name="profile"),
    path('jobs/', jobs),
    path('applogin/', applogin,name = "applogin"),
    path('appsignup/', appsignup,name="appsignup"),
    path('hrlogin/',hrlogin,name = "hrlogin"),
    path('hrsignup/',hrsignup,name="hrsignup"),
    path('manage/', manage,name="manage"),
    path('quiz/', quiz),
    path('compare/', compare,name="compare"),
    path('interview/', interview,name="interview"),
    path('analyse/', analyse,name="analyse"),
    path('resume_upload/',resume_upload, name="resume_upload"),
    path('logout/', logout, name='logout'),
    path('appquiz/', appquiz, name='appquiz'),
    path('batch/',batch,name="batch")
]
