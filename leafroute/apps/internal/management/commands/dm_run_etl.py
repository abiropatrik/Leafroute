from django.core.management.base import BaseCommand
from leafroute.etl_jobs.etl_job import dm_etl_job

class Command(BaseCommand):
    help = 'Run the ETL job to transfer data from internal to internal_dm'

    def handle(self, *args, **kwargs):
        dm_etl_job()