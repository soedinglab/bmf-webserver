from django import forms
from .models import BMFJob

class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)

class BMFInput(forms.ModelForm):
    class Meta:
        model = BMFJob
        fields = [
            'job_name',
            'ps_seqs',
            'bg_seqs',
            'input_type',
            'core_size',
            'max_iterations',
            'no_tries'
        ]

        labels = {
            'job_name':'Job name',
            'ps_seqs':'Enriched sequences',
            'bg_seqs':'Background sequences',
            'input_type':'File format',
            'core_size':'Motif core size',
            'max_iterations':'Maximum iterations',
            'no_tries':'Number of tries'
        }

class JobsearchForm(forms.Form):
    job_id = forms.UUIDField(label='Job ID')