import random
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
from users.models import User
from subscriptions.models import Subscription


class Command(BaseCommand):
    help = 'Generates clean fake data for users and subscriptions'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write('Deleting old data...')
        Subscription.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write('Creating new data...')
        fake = Faker()

        users = []
        for i in range(10):
            email = f'user{i + 1}@example.com'
            password = 'password123'
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'password': password}
            )
            if created:
                user.set_password(password)
                user.save()
            users.append(user)

        cities = [
            'London',
            'Paris',
            'New York',
            'Tokyo', 'Sydney',
            'Berlin',
            'Kyiv',
            'Dubai',
            'Toronto',
            'Rome'
        ]

        for user in users:
            for _ in range(random.randint(1, 3)):
                city = random.choice(cities)

                if not Subscription.objects.filter(user=user, city=city, is_active=True).exists():

                    method = random.choice(['email', 'webhook'])
                    url = None
                    if method == 'webhook':
                        url = fake.url()

                    Subscription.objects.create(
                        user=user,
                        city=city,
                        notification_period=random.choice([1, 3, 6, 12]),
                        notification_method=method,
                        webhook_url=url,
                        is_active=True
                    )
        self.stdout.write(self.style.SUCCESS('Successfully seeded the database with clean data.'))