from django.db import models
import uuid
from django.utils import timezone
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
import os
import shutil

from logging import getLogger

logger = getLogger(__name__)

job_fs = FileSystemStorage(location=settings.JOB_DIR)

file_formats = [
    ('fasta','fasta'),
    ('fastq','fastq'),
    ('seq','seq')
]
class Name(models.Model):
    name = models.CharField(max_length=30)

def job_upload(bmf_job, file_name):
    return os.path.join(str(bmf_job.job_id), 'input', file_name)

def file_size_validator(file):
    if file.size > settings.MAX_UPLOAD_FILE_SIZE:
        raise ValidationError('Oops! File size exceeds upload limit!')

class BMFJob(models.Model):
    job_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job_name = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50, default='queueing')
    completed = models.BooleanField(default=False)
    ps_seqs = models.FileField(upload_to=job_upload, storage=job_fs, validators=[file_size_validator])
    bg_seqs = models.FileField(upload_to=job_upload, storage=job_fs, validators=[file_size_validator])
    core_size = models.PositiveSmallIntegerField(default=3)
    max_iterations = models.PositiveSmallIntegerField(default=1000)
    no_tries = models.PositiveSmallIntegerField(default=1)
    input_type = models.CharField(choices=file_formats, default='fasta', max_length=20)
    is_bipartite = models.BooleanField(default=False, null=True)
    is_example = models.BooleanField(default=False, null=True)

    @property
    def ps_file_path(self):
        return self.ps_seqs.storage.path(self.ps_seqs.name)

    @property
    def bg_file_path(self):
        return self.bg_seqs.storage.path(self.bg_seqs.name)

    @property
    def output_prefix_name(self):
        ps_name = os.path.basename(self.ps_seqs.name)
        ps_name = os.path.splitext(ps_name)[0]
        return ps_name

    @property
    def output_prefix(self):
        ps_name = self.output_prefix_name
        return job_fs.path(os.path.join(str(self.job_id), 'output', ps_name))

    @property
    def output_prefix_relpath(self):
        return os.path.join(self.output_relpath, self.output_prefix_name)

    @property
    def output_relpath(self):
        return os.path.join('jobs', str(self.job_id), 'output')

    @property
    def job_path(self):
        return job_fs.path(str(self.job_id))

    @property
    def log_path(self):
        return job_fs.path(os.path.join(str(self.job_id), 'log.out'))


@receiver(post_delete, sender=BMFJob)
def delete_job(sender, instance, *args, **kwargs):
    job_dir = instance.job_path
    if os.path.isdir(job_dir):
        try:
            shutil.rmtree(job_dir)
            logger.debug('cleaned up job dir %s from file storage', job_dir)
        except Exception as exc:
            logger.error(exc)

@receiver(pre_save, sender=BMFJob)
def save_job(sender, instance, *args, **kwargs):
    job_dir = instance.job_path
    os.makedirs(os.path.join(job_dir,'input'), exist_ok=True)
    os.makedirs(os.path.join(job_dir,'output'), exist_ok=True)
