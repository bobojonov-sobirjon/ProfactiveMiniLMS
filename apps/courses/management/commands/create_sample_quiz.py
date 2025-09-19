from django.core.management.base import BaseCommand
from apps.courses.models import Courses, CourseQuiz, QuizQuestion


class Command(BaseCommand):
    help = 'Create sample quiz data for testing'

    def handle(self, *args, **options):
        # Get the first course
        try:
            course = Courses.objects.first()
            if not course:
                self.stdout.write(
                    self.style.ERROR('No courses found. Please create a course first.')
                )
                return
        except Courses.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('No courses found. Please create a course first.')
            )
            return

        # Create quiz for the course
        quiz, created = CourseQuiz.objects.get_or_create(
            course=course,
            defaults={
                'title': f'Тест по курсу "{course.name}"',
                'description': 'Проверьте свои знания по пройденному материалу',
                'passing_score': 70,
                'time_limit': 30,
                'questions_count': 10,
                'is_active': True
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created quiz: {quiz.title}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Quiz already exists: {quiz.title}')
            )

        # Create sample questions
        sample_questions = [
            {
                'question_text': 'Что такое Django?',
                'option_a': 'Язык программирования',
                'option_b': 'Веб-фреймворк для Python',
                'option_c': 'База данных',
                'option_d': 'Операционная система',
                'correct_answer': 'B',
                'explanation': 'Django - это высокоуровневый веб-фреймворк для Python.'
            },
            {
                'question_text': 'Какой метод используется для создания миграций в Django?',
                'option_a': 'python manage.py migrate',
                'option_b': 'python manage.py makemigrations',
                'option_c': 'python manage.py runserver',
                'option_d': 'python manage.py collectstatic',
                'correct_answer': 'B',
                'explanation': 'makemigrations создает файлы миграций, а migrate применяет их.'
            },
            {
                'question_text': 'Что такое ORM в Django?',
                'option_a': 'Объектно-реляционное отображение',
                'option_b': 'Операционная система',
                'option_c': 'Язык программирования',
                'option_d': 'База данных',
                'correct_answer': 'A',
                'explanation': 'ORM позволяет работать с базой данных через объекты Python.'
            },
            {
                'question_text': 'Какой файл содержит настройки Django проекта?',
                'option_a': 'models.py',
                'option_b': 'views.py',
                'option_c': 'settings.py',
                'option_d': 'urls.py',
                'correct_answer': 'C',
                'explanation': 'settings.py содержит все настройки Django проекта.'
            },
            {
                'question_text': 'Что такое middleware в Django?',
                'option_a': 'База данных',
                'option_b': 'Промежуточное ПО для обработки запросов',
                'option_c': 'Шаблон',
                'option_d': 'Модель',
                'correct_answer': 'B',
                'explanation': 'Middleware обрабатывает запросы и ответы на промежуточном уровне.'
            },
            {
                'question_text': 'Как создать суперпользователя в Django?',
                'option_a': 'python manage.py createsuperuser',
                'option_b': 'python manage.py createuser',
                'option_c': 'python manage.py superuser',
                'option_d': 'python manage.py admin',
                'correct_answer': 'A',
                'explanation': 'createsuperuser создает администратора Django.'
            },
            {
                'question_text': 'Что такое MVT в Django?',
                'option_a': 'Model-View-Template',
                'option_b': 'Model-View-Controller',
                'option_c': 'Many-Very-Template',
                'option_d': 'Model-Very-Template',
                'correct_answer': 'A',
                'explanation': 'Django использует архитектуру Model-View-Template.'
            },
            {
                'question_text': 'Как запустить сервер разработки Django?',
                'option_a': 'python manage.py startserver',
                'option_b': 'python manage.py runserver',
                'option_c': 'python manage.py server',
                'option_d': 'python manage.py dev',
                'correct_answer': 'B',
                'explanation': 'runserver запускает встроенный сервер разработки.'
            },
            {
                'question_text': 'Что такое URLconf в Django?',
                'option_a': 'Конфигурация URL-ов',
                'option_b': 'База данных',
                'option_c': 'Шаблон',
                'option_d': 'Модель',
                'correct_answer': 'A',
                'explanation': 'URLconf определяет, какие URL-ы обрабатываются какими представлениями.'
            },
            {
                'question_text': 'Как получить объект по ID в Django ORM?',
                'option_a': 'Model.objects.get(id=1)',
                'option_b': 'Model.objects.filter(id=1)',
                'option_c': 'Model.objects.all(id=1)',
                'option_d': 'Model.objects.find(id=1)',
                'correct_answer': 'A',
                'explanation': 'get() возвращает один объект, filter() возвращает QuerySet.'
            }
        ]

        created_count = 0
        for i, question_data in enumerate(sample_questions):
            question, created = QuizQuestion.objects.get_or_create(
                quiz=quiz,
                question_text=question_data['question_text'],
                defaults={
                    'option_a': question_data['option_a'],
                    'option_b': question_data['option_b'],
                    'option_c': question_data['option_c'],
                    'option_d': question_data['option_d'],
                    'correct_answer': question_data['correct_answer'],
                    'explanation': question_data['explanation'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Created {created_count} questions for quiz: {quiz.title}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Total questions in quiz: {quiz.quizquestion_set.count()}')
        )
