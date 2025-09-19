from django.core.management.base import BaseCommand
from apps.website.models import AboutPage, Mission, MissionPoint, Value


class Command(BaseCommand):
    help = 'Заполнить страницу о нас тестовыми данными'

    def handle(self, *args, **options):
        # Создать данные AboutPage
        about_page, created = AboutPage.objects.get_or_create(
            title="О",
            defaults={
                'subtitle': "нас",
                'description': "Profactive - это современный учебный центр, который предоставляет качественное образование и профессиональную подготовку для всех желающих развиваться и достигать новых высот.",
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Успешно создана страница о нас')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Страница о нас уже существует')
            )

        # Создать данные Mission
        mission, created = Mission.objects.get_or_create(
            title="Наша миссия",
            defaults={
                'description': "Мы стремимся сделать качественное образование доступным для каждого, предоставляя современные методы обучения и индивидуальный подход к каждому студенту.",
                'achievement_number': "100+",
                'achievement_text': "Успешных выпускников",
                'is_active': True,
                'order': 1
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Успешно создана миссия')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Миссия уже существует')
            )

        # Создать пункты миссии
        mission_points_data = [
            "Качественное образование",
            "Современные методы обучения", 
            "Индивидуальный подход"
        ]
        
        for i, point_text in enumerate(mission_points_data, 1):
            point, created = MissionPoint.objects.get_or_create(
                mission=mission,
                text=point_text,
                defaults={
                    'order': i,
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Успешно создан пункт миссии: {point_text}')
                )

        # Создать данные о ценностях
        values_data = [
            {
                'title': 'Качество',
                'description': 'Высокие стандарты образования и постоянное совершенствование',
                'icon_svg': '<svg class="w-8 h-8 text-primary" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>',
                'order': 1
            },
            {
                'title': 'Инновации',
                'description': 'Современные технологии и методы обучения',
                'icon_svg': '<svg class="w-8 h-8 text-primary" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>',
                'order': 2
            },
            {
                'title': 'Поддержка',
                'description': 'Индивидуальная поддержка каждого студента',
                'icon_svg': '<svg class="w-8 h-8 text-primary" fill="currentColor" viewBox="0 0 24 24"><path d="M16 4c0-1.11.89-2 2-2s2 .89 2 2-.89 2-2 2-2-.89-2-2zm4 18v-6h2.5l-2.54-7.63A1.5 1.5 0 0 0 18.54 8H16c-.8 0-1.54.37-2.01.99L12 11l-1.99-2.01A2.5 2.5 0 0 0 8 8H5.46c-.8 0-1.54.37-2.01.99L1 14.37V22h2v-6h2.5l2.54 7.63A1.5 1.5 0 0 0 9.46 24H11c.8 0 1.54-.37 2.01-.99L15 21l1.99 2.01A2.5 2.5 0 0 0 19 24h2.54c.8 0 1.54-.37 2.01-.99L24 16.37V22h2z"/></svg>',
                'order': 3
            }
        ]
        
        for value_data in values_data:
            value, created = Value.objects.get_or_create(
                title=value_data['title'],
                defaults={
                    'description': value_data['description'],
                    'icon_svg': value_data['icon_svg'],
                    'is_active': True,
                    'order': value_data['order']
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Успешно создана ценность: {value_data["title"]}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Ценность уже существует: {value_data["title"]}')
                )

        self.stdout.write(
            self.style.SUCCESS('Успешно заполнены данные страницы о нас!')
        )
