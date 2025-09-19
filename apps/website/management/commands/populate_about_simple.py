from django.core.management.base import BaseCommand
from apps.website.models import AboutSection


class Command(BaseCommand):
    help = 'Заполнить страницу о нас простыми данными'

    def handle(self, *args, **options):
        # Удалить старые данные
        AboutSection.objects.all().delete()
        
        # Создать секции
        sections_data = [
            {
                'title': 'Profactive: Ваш ключ к новым возможностям!',
                'description': 'Устали стоять на месте? Хотите освоить востребованную профессию, повысить свою квалификацию или просто расширить горизонты знаний? Учебный центр Profactive – это место, где ваши амбиции обретают реальные формы. Мы предлагаем современные, практико-ориентированные курсы, разработанные ведущими экспертами в своих областях. Учитесь у лучших, достигайте большего с Profactive!',
                'keywords': 'Profactive, ключ, возможностям',
                'button_text': 'Узнать подробнее',
                'button_url': '#',
                'order': 1
            },
            {
                'title': 'Инвестируйте в свое будущее',
                'description': 'Хотите сделать уверенный шаг вперед в карьере? Мечтаете о повышении или смене сферы деятельности? Учебный центр Profactive поможет вам достичь ваших карьерных целей. Мы предлагаем актуальные образовательные программы, которые соответствуют требованиям рынка труда. Получите знания и навыки, которые откроют вам двери к новым возможностям и успешному будущему. Profactive – ваш надежный партнер в развитии!',
                'keywords': 'Инвестируйте, будущее',
                'order': 2
            },
            {
                'title': 'Обучение для вашего успеха',
                'description': 'Получите востребованные знания и практические навыки в учебном центре Profactive. Мы предлагаем современные курсы для вашего профессионального и личностного роста. Учитесь с нами, достигайте большего!\n\nВ современном мире важно не просто учиться, а учиться эффективно. В учебном центре Profactive мы делаем ставку на практические навыки и реальные результаты. Наши программы построены таким образом, чтобы вы могли сразу же применять полученные знания в работе и жизни. Откройте для себя новые перспективы и станьте востребованным специалистом вместе с Profactive!',
                'keywords': 'Обучение, успеха',
                'order': 3
            }
        ]
        
        for section_data in sections_data:
            section = AboutSection.objects.create(
                title=section_data['title'],
                description=section_data['description'],
                keywords=section_data['keywords'],
                button_text=section_data.get('button_text'),
                button_url=section_data.get('button_url'),
                is_active=True,
                order=section_data['order']
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Успешно создана секция {section_data["order"]}: {section_data["title"][:50]}...')
            )

        self.stdout.write(
            self.style.SUCCESS('Успешно заполнены данные страницы о нас!')
        )
