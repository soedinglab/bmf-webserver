from django.core.management.base import BaseCommand
import os
from bmf.models import BMFJob
from bmf.tasks import bmf_task
import logging
import uuid
from django.core.files import File

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--flush', action='store_true')

    def handle(self, *args, **options):

        if options['flush']:
            for example_job in BMFJob.objects.filter(is_example=True):
                logger.info('Removing example job %s', example_job)
                example_job.delete()

        if BMFJob.objects.filter(pk=uuid.UUID(int=0)).exists():
            return

        job = BMFJob(
                job_id = uuid.UUID(int=0),
                job_name = 'Example Job',
                is_example = True
        )

        example_bg_file = 'example_files/negatives_AAA_CCC.fasta'
        with open(example_bg_file) as fh:
            job.bg_seqs.save(os.path.basename(example_bg_file), File(fh))

        example_ps_file = 'example_files/positives_AAA_CCC.fasta'
        with open(example_ps_file) as fh:
            job.ps_seqs.save(os.path.basename(example_ps_file), File(fh))

        job.save()
        bmf_task.delay(job.job_id)
