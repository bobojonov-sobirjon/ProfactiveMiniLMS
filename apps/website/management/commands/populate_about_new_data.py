from django.core.management.base import BaseCommand
from apps.website.models import AboutPage, AboutSection


class Command(BaseCommand):
    help = 'Заполнить новую страницу о нас тестовыми данными'

    def handle(self, *args, **options):
        # Создать AboutPage
        about_page, created = AboutPage.objects.get_or_create(
            title="О нас",
            defaults={
                'subtitle': "Получайте 16% с каждой продажи!",
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

        # Создать секции
        sections_data = [
            {
                'title': '<span class="text-gradient-display">Profactive: Ваш ключ </span>к новым возможностям!',
                'description': 'Устали стоять на месте? Хотите освоить востребованную профессию, повысить свою квалификацию или просто расширить горизонты знаний? Учебный центр Profactive – это место, где ваши амбиции обретают реальные формы. Мы предлагаем современные, практико-ориентированные курсы, разработанные ведущими экспертами в своих областях. Учитесь у лучших, достигайте большего с Profactive!',
                'button_text': 'Узнать подробнее',
                'button_url': '#',
                'order': 1
            },
            {
                'title': 'Инвестируйте <span class="text-gradient-display">в свое будущее</span>',
                'description': 'Хотите сделать уверенный шаг вперед в карьере? Мечтаете о повышении или смене сферы деятельности? Учебный центр Profactive поможет вам достичь ваших карьерных целей. Мы предлагаем актуальные образовательные программы, которые соответствуют требованиям рынка труда. Получите знания и навыки, которые откроют вам двери к новым возможностям и успешному будущему. Profactive – ваш надежный партнер в развитии!',
                'button_text': '',
                'button_url': '',
                'order': 2
            },
            {
                'title': '<span class="text-gradient-display">Обучение</span> для вашего успеха',
                'description': 'Получите востребованные знания и практические навыки в учебном центре Profactive. Мы предлагаем современные курсы для вашего профессионального и личностного роста. Учитесь с нами, достигайте большего!\n\nВ современном мире важно не просто учиться, а учиться эффективно. В учебном центре Profactive мы делаем ставку на практические навыки и реальные результаты. Наши программы построены таким образом, чтобы вы могли сразу же применять полученные знания в работе и жизни. Откройте для себя новые перспективы и станьте востребованным специалистом вместе с Profactive!',
                'button_text': '',
                'button_url': '',
                'order': 3
            }
        ]
        
        for section_data in sections_data:
            section, created = AboutSection.objects.get_or_create(
                about_page=about_page,
                order=section_data['order'],
                defaults={
                    'title': section_data['title'],
                    'description': section_data['description'],
                    'button_text': section_data['button_text'] if section_data['button_text'] else None,
                    'button_url': section_data['button_url'] if section_data['button_url'] else None,
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Успешно создана секция {section_data["order"]}: {section_data["title"][:50]}...')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Секция {section_data["order"]} уже существует')
                )

        self.stdout.write(
            self.style.SUCCESS('Успешно заполнены данные новой страницы о нас!')
        )
