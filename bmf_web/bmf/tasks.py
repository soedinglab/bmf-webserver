from celery.exceptions import SoftTimeLimitExceeded
from django.utils import timezone
import traceback
import sys
import subprocess
from contextlib import redirect_stderr, redirect_stdout
from celery import task
from .models import BMFJob
from bmf_tool.utils import is_bipartite, prefix2params

import logging
logger = logging.getLogger(__name__)

class JobSaveManager:

    def __init__(self, job, success_status='Success', error_status='Error'):
        self.error_status = error_status
        self.success_status = success_status
        self.job = job

    def __enter__(self):
        return self

    def __exit__(self, error_type, error, tb):
        job = self.job

        swallow_exception = False

        if error_type is SoftTimeLimitExceeded:
            job.status = 'Killed'
            self.had_exception = True
            print(timezone.now(), "\t | WARNING: \t Exceeded time limit.")
            logger.warn('Job %s exceeded the time limit and was killed.', job.pk)
            swallow_exception = True

        elif error_type is not None:
            job.status = self.error_status
            self.had_exception = True
            logger.exception(error)
            traceback.print_exception(error_type, error, tb, file=sys.stdout)
            print(timezone.now(), "\t | WARNING: \t %s " % job.status)
            swallow_exception = True

        else:
            job.status = self.success_status
            self.had_exception = False
            print(timezone.now(), "\t | END: \t %s " % job.status)

        job.save()
        return swallow_exception


def run_command(command, enforce_exit_zero=True, cwd=None):

    command = [str(s) for s in command]

    command_str = ' '.join('%r' % s for s in command)
    logger.debug("executing: %s", command_str)

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd)
    while True:
        nextline = process.stdout.readline()
        if nextline == b'' and process.poll() is not None:
            break
        print(nextline.decode('utf-8'), file=sys.stdout, end='')
        sys.stdout.flush()
    process.wait()

    if enforce_exit_zero:
        if process.returncode != 0:
            raise CommandFailureException(command_str)

    return process.returncode

class CommandFailureException(Exception):
    pass

def get_bmf_command(bmf_job):

    ps_file_path = bmf_job.ps_file_path
    bg_file_path = bmf_job.bg_file_path
    core_size = bmf_job.core_size
    max_iterations = bmf_job.max_iterations
    no_tries = bmf_job.no_tries
    input_type = bmf_job.input_type
    output_prefix = bmf_job.output_prefix

    command = [
        'bmf', ps_file_path, 
        '--BGsequences', bg_file_path, 
        '--input_type', input_type, 
        '--max_iterations', max_iterations, 
        '--no_tries', no_tries,
        '--motif_length', core_size,
        '--output_prefix', output_prefix
    ]

    return command

def get_logoplot_command(bmf_job):

    core_size = bmf_job.core_size
    output_prefix = bmf_job.output_prefix

    command = [
        'bmf_logo', output_prefix, 
        '--motif_length', core_size
    ]

    return command


def get_compress_command(job):

    command = [
        'zip', 
        '-r', 
        f'{job.job_id}.zip',
        '.'
    ]

    return command


@task(bind=True)
def bmf_task(self, job_id):
    job = BMFJob.objects.get(pk=job_id)
    with JobSaveManager(job), open(job.log_path, 'a') as log:
        job.status = 'running BMF'
        job.save()
        with redirect_stdout(log), redirect_stderr(log):
            run_command(get_bmf_command(job))
            run_command(get_logoplot_command(job))
            params = prefix2params(job.output_prefix, job.core_size)
            job.is_bipartite = is_bipartite(params, job.core_size)
            run_command(get_compress_command(job), cwd=job.job_path)
        job.completed = True
    




