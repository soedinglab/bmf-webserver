from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.utils.html import escape
from . import forms
from .utils import check_input_file
from .models import Name, BMFJob
from .tasks import bmf_task
import os
import glob
import re


# Create your views here.

def home(request):
    return render(request, 'home.html', {'page':'home'})

def jobid_to_results(request):
    form = forms.JobsearchForm(request.POST)
    if form.is_valid():
        job_id = form.cleaned_data['job_id']
        if BMFJob.objects.filter(pk=job_id).exists():
            return redirect('show_results', job_id=job_id)
    
    job_id = form['job_id'].data
    return render(request, 'job_not_found.html', {'job_id': job_id})

def run_bmf(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = forms.BMFInput(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(commit=False)

            ps_file_is_valid = check_input_file(job, form, request.FILES, 'ps_seqs')
            bg_file_is_valid = check_input_file(job, form, request.FILES, 'bg_seqs')

            if ps_file_is_valid and bg_file_is_valid:
                job = form.save(commit=True)
                bmf_task.delay(job.job_id)
                return redirect('show_results', job_id=job.job_id)

            else:
                page = 'submit'
                return render(request, 'run_bmf.html', {'form': form, 'page':page})

    else:
        form = forms.BMFInput()

    page = 'submit'
    return render(request, 'run_bmf.html', {'form': form, 'page':page})


def show_results(request, job_id):
    job = get_object_or_404(BMFJob, pk=job_id)
    if job.completed:
        return render(request, 'show_results_completed.html', {'job': job})
    else:
        png_files = glob.glob(job.output_prefix + f'_cs{job.core_size}_*.png')
        pattern = re.compile('_([0-9]+).png$')
        
        highest_iter = -1
        current_file = None
        for png_file in png_files:
            hit = pattern.search(png_file)
            if hit is not None:
                if int(hit.group(1)) >highest_iter:
                    current_file = png_file
                    highest_iter = int(hit.group(1))

        if current_file is not None:
            _ , file_name = os.path.split(current_file)
        else:
            file_name = None

        log_text = ''
        log_file_path = os.path.join(job.job_path, 'log.out')
        if os.path.exists(log_file_path):
            with open(log_file_path) as f:
                log_text = f.read()
                log_text = escape(log_text)
                #log_text = log_text.replace('\n',' <br /> ')
        return render(request, 'show_results_running.html', {'job': job, 'current_file':file_name, 'log_content':log_text})

    
def download_results(request, job_id):
    job = get_object_or_404(BMFJob, pk=job_id)
    file_path = os.path.join(job.job_path, f'{job_id}.zip')
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/zip")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404

def contact(request):
    return render(request, 'contact.html')

def imprint(request):
    return render(request, 'imprint.html')