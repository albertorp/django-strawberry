from decimal import Decimal
import random
from faker import Faker
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from sampleapp.models import SampleModel, Country

class Command(BaseCommand):
    help = 'Generate a specified number of random samples in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--num_samples',
            type=int,
            nargs='?',  # This makes the argument optional
            default=10,  # This is the default value if no argument is provided
            help='Indicates the number of samples to be created (default: 10)',
        )

    def handle(self, *args, **options):
        num_samples = options['num_samples']
        fake = Faker()
        countries = {
            ('Spain', 'ES'),
            ('United States', 'US'),
            ('France', 'FR'),
            ('Germany', 'DE'),
            ('Italy', 'IT'),
            ('China', 'CN'),
            ('Japan', 'JP'),
            ('India', 'IN'),
            ('Brazil', 'BR'),
            ('United Arab Emirates', 'AE'),
            ('United Kingdom', 'UK'),
            ('Canada', 'CA'),
            ('South Korea', 'KR'),
            ('Mexico', 'MX'),
            ('Argentina', 'AR'),
            ('Netherlands', 'NL'),
            ('Sweden', 'SE'),
            ('Norway', 'NO'),
            ('Denmark', 'DK'),
            ('Finland', 'FI'),
            ('Russia', 'RU'),
            ('South Africa', 'ZA'),
            ('Egypt', 'EG'),
            ('Turkey', 'TR'),
            ('Saudi Arabia', 'SA'),
            ('Pakistan', 'PK'),
            ('Indonesia', 'ID'),
            ('Malaysia', 'MY'),
            ('Thailand', 'TH'),
            ('Philippines', 'PH'),
        }

        for country in countries:
            Country.objects.get_or_create(name=country[0], iso_code=country[1])

        countries = Country.objects.all()
        statuses = [x[0] for x in SampleModel.STATUS_CHOICES]

        # get the user
        User = get_user_model()
        user = User.objects.filter(username='arodriguezprieto@gmail.com').first()
        if not user:
            user = User.objects.create_superuser('arodriguezprieto@gmail.com', 'arodriguezprieto@gmail.com', 'Cust0mer,')

        for i in range(num_samples):
            sample = SampleModel.objects.create(
                user=user,
                name=fake.name(),
                email=fake.email(),
                country=random.choice(countries),
                integer=random.uniform(1, 1000),
                decimal = Decimal(random.uniform(1, 1000)),
                date=fake.date_between(start_date='-1y', end_date='today'),
                description=fake.text(50),
                status=random.choice(statuses)
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created sample with ID {sample.id}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_samples} samples'))
           