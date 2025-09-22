from django.core.management.base import BaseCommand
from apps.website.models import Blog
from django.core.files.base import ContentFile
import os

class Command(BaseCommand):
    help = 'Populate blog with sample data'

    def handle(self, *args, **options):
        # Sample blog data
        blog_data = [
            {
                'title': 'Повышение квалификации',
                'description': 'Заполните форму, скопируйте ссылку, отправьте ее личным сообщением. Получите скидку с каждой продажи! Это отличная возможность для дополнительного заработка.',
                'image_path': 'static/assets/images/main-hero.png'
            },
            {
                'title': 'Новые технологии в образовании',
                'description': 'Современные подходы к обучению и развитию навыков. Изучайте новые методы преподавания и повышайте эффективность образовательного процесса.',
                'image_path': 'static/assets/images/popular-1.jpg'
            },
            {
                'title': 'Карьерный рост и развитие',
                'description': 'Как правильно строить карьеру в современном мире. Практические советы и рекомендации от экспертов в области HR и карьерного консультирования.',
                'image_path': 'static/assets/images/popular-2.jpg'
            },
            {
                'title': 'Удаленная работа: плюсы и минусы',
                'description': 'Анализ преимуществ и недостатков удаленной работы. Как организовать эффективное рабочее пространство дома и поддерживать продуктивность.',
                'image_path': 'static/assets/images/popular-3.png'
            },
            {
                'title': 'Цифровые навыки будущего',
                'description': 'Какие навыки будут востребованы в ближайшие 5-10 лет. Изучайте актуальные технологии и развивайтесь в правильном направлении.',
                'image_path': 'static/assets/images/popular-5.jpg'
            },
            {
                'title': 'Личная эффективность и тайм-менеджмент',
                'description': 'Как правильно планировать время и достигать поставленных целей. Практические техники управления временем и повышения личной эффективности.',
                'image_path': 'static/assets/images/popular-6.png'
            },
            {
                'title': 'Финансовая грамотность',
                'description': 'Основы управления личными финансами. Как правильно инвестировать, планировать бюджет и достигать финансовых целей.',
                'image_path': 'static/assets/images/referall-img(2).png'
            },
            {
                'title': 'Здоровый образ жизни',
                'description': 'Как совмещать работу и заботу о здоровье. Практические советы по поддержанию физической и ментальной формы в условиях современного ритма жизни.',
                'image_path': 'static/assets/images/referall-img(3).png'
            },
            {
                'title': 'Сетевой маркетинг и продажи',
                'description': 'Эффективные стратегии продаж и построения клиентской базы. Как развивать бизнес через социальные сети и личные контакты.',
                'image_path': 'static/assets/images/referall-img(4).png'
            }
        ]

        # Clear existing blogs
        Blog.objects.all().delete()
        self.stdout.write('Cleared existing blog data')

        # Create new blogs
        for i, data in enumerate(blog_data):
            blog = Blog.objects.create(
                title=data['title'],
                description=data['description'],
                is_active=True
            )
            
            # Copy image file if it exists
            image_path = data['image_path']
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    blog.image.save(
                        os.path.basename(image_path),
                        ContentFile(f.read()),
                        save=True
                    )
            
            self.stdout.write(f'Created blog: {blog.title}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(blog_data)} blog posts')
        )
