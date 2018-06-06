import json
from django.core.management.base import BaseCommand, CommandError
import requests


class Command(BaseCommand):
    help = 'Create form for kpi'

    def handle(self, *args, **options):
        settings =  {"description":"sumeet desc","sector":"","country":"","share-metadata":False}
        headers = {"Authorization": "Token 536680a582ae63cf801b133a1dbe666d5f332ef7", "Content-Type":"application/json"}
        payload = dict(settings=settings, name="hello", asset_type="survey" )
        r = requests.post('http://192.168.1.111:8000/assets/', data=payload,  headers=headers)
