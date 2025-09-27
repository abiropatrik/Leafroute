from django.core.management.base import BaseCommand
from leafroute.etl_jobs.etl_job import etl_job

class Command(BaseCommand):
    help = 'Run the ETL job to transfer data from internal_stage to internal'

    def handle(self, *args, **kwargs):
        etl_job()