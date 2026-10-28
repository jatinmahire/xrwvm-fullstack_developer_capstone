"""Idempotent import of the starter catalogue and optional demo accounts."""
import json
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from djangoapp.models import CarMake, CarModel
class Command(BaseCommand):
    help = 'Populate car catalogue and optional environment-configured demo accounts.'
    def handle(self, *args, **options):
        data = json.loads((Path(__file__).resolve().parents[3]/'database/data/car_records.json').read_text())
        for item in data['cars']:
            make, _ = CarMake.objects.get_or_create(name=item['make'], defaults={'description':f"Vehicles manufactured by {item['make']}."})
            CarModel.objects.get_or_create(car_make=make, name=item['model'], year=item['year'], defaults={'type':item.get('bodyType','Other')})
        for username, password, admin in [
            (os.environ.get('DEMO_USERNAME','learner'), os.environ.get('DEMO_PASSWORD'), False),
            ('root', os.environ.get('DEMO_ADMIN_PASSWORD'), True)]:
            if password and not User.objects.filter(username=username).exists():
                User.objects.create_user(username=username, email=f'{username}@example.com', password=password,
                    first_name='Capstone', last_name='Learner', is_staff=admin, is_superuser=admin)
        self.stdout.write(self.style.SUCCESS(f'Catalogue ready: {CarMake.objects.count()} makes, {CarModel.objects.count()} models.'))
