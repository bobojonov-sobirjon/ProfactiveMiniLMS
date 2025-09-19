from django.core.management.base import BaseCommand
from apps.courses.models import Categories, Courses, CourseMaterials


class Command(BaseCommand):
    help = 'Populate courses with sample data'

    def handle(self, *args, **options):
        # Create main categories
        programming_cat, created = Categories.objects.get_or_create(
            name="Программирование",
            defaults={'parent': None, 'icon': 'category_icons/programming_icon.svg'}
        )

        design_cat, created = Categories.objects.get_or_create(
            name="Дизайн",
            defaults={'parent': None, 'icon': 'category_icons/design_icon.svg'}
        )

        marketing_cat, created = Categories.objects.get_or_create(
            name="Маркетинг",
            defaults={'parent': None, 'icon': 'category_icons/marketing_icon.svg'}
        )

        education_cat, created = Categories.objects.get_or_create(
            name="Образование",
            defaults={'parent': None, 'icon': 'category_icons/education_icon.svg'}
        )

        business_cat, created = Categories.objects.get_or_create(
            name="Бизнес",
            defaults={'parent': None, 'icon': 'category_icons/business_icon.svg'}
        )

        # Create subcategories
        web_dev_cat, created = Categories.objects.get_or_create(
            name="Веб-разработка",
            defaults={'parent': programming_cat}
        )

        graphic_design_cat, created = Categories.objects.get_or_create(
            name="Графический дизайн",
            defaults={'parent': design_cat}
        )

        ui_ux_cat, created = Categories.objects.get_or_create(
            name="UI/UX дизайн",
            defaults={'parent': design_cat}
        )

        digital_marketing_cat, created = Categories.objects.get_or_create(
            name="Цифровой маркетинг",
            defaults={'parent': marketing_cat}
        )

        smm_cat, created = Categories.objects.get_or_create(
            name="SMM",
            defaults={'parent': marketing_cat}
        )

        # Create courses
        course1, created = Courses.objects.get_or_create(
            name="Веб-разработка с нуля",
            defaults={
                'description': 'Полный курс по веб-разработке. Изучите HTML, CSS, JavaScript, Python и Django. Создайте свой первый веб-сайт и получите навыки для работы в IT.',
                'author': 'Иван Петров',
                'category': web_dev_cat,
                'is_popular': True
            }
        )

        course2, created = Courses.objects.get_or_create(
            name="Графический дизайн",
            defaults={
                'description': 'Освойте основы графического дизайна. Изучите Adobe Photoshop, Illustrator, принципы композиции и цветоведения.',
                'author': 'Анна Смирнова',
                'category': graphic_design_cat,
                'is_popular': True
            }
        )

        course3, created = Courses.objects.get_or_create(
            name="Цифровой маркетинг",
            defaults={
                'description': 'Современные стратегии цифрового маркетинга. SMM, контекстная реклама, SEO, email-маркетинг и аналитика.',
                'author': 'Михаил Козлов',
                'category': digital_marketing_cat,
                'is_popular': True
            }
        )

        # Create additional popular courses
        course4, created = Courses.objects.get_or_create(
            name="Python для начинающих",
            defaults={
                'description': 'Изучите основы программирования на Python. От простых скриптов до веб-приложений.',
                'author': 'Алексей Иванов',
                'category': programming_cat,
                'is_popular': True
            }
        )

        course5, created = Courses.objects.get_or_create(
            name="UI/UX дизайн",
            defaults={
                'description': 'Создавайте удобные и красивые интерфейсы. Изучите принципы пользовательского опыта.',
                'author': 'Мария Петрова',
                'category': ui_ux_cat,
                'is_popular': True
            }
        )

        course6, created = Courses.objects.get_or_create(
            name="SMM продвижение",
            defaults={
                'description': 'Эффективное продвижение в социальных сетях. Instagram, Facebook, VKontakte.',
                'author': 'Дмитрий Смирнов',
                'category': smm_cat,
                'is_popular': True
            }
        )

        # Create 10 additional courses
        course7, created = Courses.objects.get_or_create(
            name="JavaScript для веб-разработки",
            defaults={
                'description': 'Изучите современный JavaScript, ES6+, асинхронное программирование и работу с DOM.',
                'author': 'Елена Козлова',
                'category': web_dev_cat,
                'is_popular': False
            }
        )

        course8, created = Courses.objects.get_or_create(
            name="Мобильная разработка на React Native",
            defaults={
                'description': 'Создавайте кроссплатформенные мобильные приложения с помощью React Native.',
                'author': 'Андрей Волков',
                'category': programming_cat,
                'is_popular': False
            }
        )

        course9, created = Courses.objects.get_or_create(
            name="3D моделирование в Blender",
            defaults={
                'description': 'Освойте 3D моделирование, анимацию и рендеринг в программе Blender.',
                'author': 'Ольга Морозова',
                'category': graphic_design_cat,
                'is_popular': False
            }
        )

        course10, created = Courses.objects.get_or_create(
            name="Анализ данных с Python",
            defaults={
                'description': 'Изучите pandas, numpy, matplotlib для анализа и визуализации данных.',
                'author': 'Сергей Новиков',
                'category': programming_cat,
                'is_popular': False
            }
        )

        course11, created = Courses.objects.get_or_create(
            name="Веб-дизайн и верстка",
            defaults={
                'description': 'Современные принципы веб-дизайна, адаптивная верстка, работа с Figma.',
                'author': 'Наталья Соколова',
                'category': ui_ux_cat,
                'is_popular': False
            }
        )

        course12, created = Courses.objects.get_or_create(
            name="Контент-маркетинг",
            defaults={
                'description': 'Создание эффективного контента для привлечения и удержания клиентов.',
                'author': 'Игорь Лебедев',
                'category': digital_marketing_cat,
                'is_popular': False
            }
        )

        course13, created = Courses.objects.get_or_create(
            name="Системное администрирование Linux",
            defaults={
                'description': 'Управление серверами Linux, настройка веб-серверов, автоматизация задач.',
                'author': 'Владимир Петров',
                'category': programming_cat,
                'is_popular': False
            }
        )

        course14, created = Courses.objects.get_or_create(
            name="Брендинг и айдентика",
            defaults={
                'description': 'Создание логотипов, фирменного стиля и брендбуков для компаний.',
                'author': 'Татьяна Кузнецова',
                'category': graphic_design_cat,
                'is_popular': False
            }
        )

        course15, created = Courses.objects.get_or_create(
            name="Email-маркетинг",
            defaults={
                'description': 'Эффективные email-кампании, автоматизация, A/B тестирование.',
                'author': 'Роман Орлов',
                'category': digital_marketing_cat,
                'is_popular': False
            }
        )

        course16, created = Courses.objects.get_or_create(
            name="Пользовательские исследования (UX Research)",
            defaults={
                'description': 'Методы исследования пользователей, интервью, тестирование интерфейсов.',
                'author': 'Анна Федорова',
                'category': ui_ux_cat,
                'is_popular': False
            }
        )

        # Create course materials for course1
        if created:
            CourseMaterials.objects.get_or_create(
                course=course1,
                title="Введение в веб-разработку",
                defaults={
                    'video_time': '00:15:30',
                    'is_activate': True,
                    'order': 1
                }
            )

        self.stdout.write(
            self.style.SUCCESS('Successfully populated courses data')
        )
