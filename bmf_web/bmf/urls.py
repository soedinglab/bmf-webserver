"""bmf_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('run_bmf', views.run_bmf, name='run_bmf'),
    path('job_id_redirect', views.jobid_to_results, name='jobid_to_results'),
    path('results/<uuid:job_id>/', views.show_results, name='show_results'),
    path('results/download/<uuid:job_id>', views.download_results, name='download_results'),
    path('contact', views.contact, name='contact'),
    path('imprint', views.imprint, name='imprint'),
]
