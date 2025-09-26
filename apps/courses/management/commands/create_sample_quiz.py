from django.core.management.base import BaseCommand
from apps.courses.models import Courses, CourseQuiz, QuizQuestion


class Command(BaseCommand):
    help = 'Create sample quiz data for testing'

    def handle(self, *args, **options):
        # Get the first course or create one
        course, created = Courses.objects.get_or_create(
            name="Python Programming Basics",
            defaults={
                'description': 'Learn the fundamentals of Python programming',
                'author': 'John Doe',
                'user_id': 1,  # Assuming admin user exists
                'category_id': 1,  # Assuming first category exists
            }
        )
        
        if created:
            self.stdout.write(f'Created course: {course.name}')
        else:
            self.stdout.write(f'Using existing course: {course.name}')

        # Create quiz
        quiz, created = CourseQuiz.objects.get_or_create(
            course=course,
            title="Python Basics Quiz",
            defaults={
                'description': 'Test your knowledge of Python programming basics',
                'questions_count': 5,
                'passing_score': 70,
                'time_limit': 10,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(f'Created quiz: {quiz.title}')
        else:
            self.stdout.write(f'Using existing quiz: {quiz.title}')

        # Sample questions
        questions_data = [
            {
                'question_text': 'What is the correct way to create a variable in Python?',
                'option_a': 'var name = "value"',
                'option_b': 'name = "value"',
                'option_c': 'variable name = "value"',
                'correct_answer': 'B',
                'explanation': 'In Python, variables are created by simply assigning a value using the = operator.'
            },
            {
                'question_text': 'Which of the following is NOT a Python data type?',
                'option_a': 'int',
                'option_b': 'string',
                'option_c': 'char',
                'correct_answer': 'C',
                'explanation': 'Python does not have a separate char data type. Characters are represented as strings of length 1.'
            },
            {
                'question_text': 'What is the output of print(3 + 2 * 4)?',
                'option_a': '20',
                'option_b': '11',
                'option_c': '14',
                'correct_answer': 'B',
                'explanation': 'Due to operator precedence, multiplication is performed first: 2 * 4 = 8, then 3 + 8 = 11.'
            },
            {
                'question_text': 'Which keyword is used to define a function in Python?',
                'option_a': 'function',
                'option_b': 'def',
                'option_c': 'func',
                'correct_answer': 'B',
                'explanation': 'The def keyword is used to define functions in Python.'
            },
            {
                'question_text': 'What will be the output of len("Hello World")?',
                'option_a': '10',
                'option_b': '11',
                'option_c': '12',
                'correct_answer': 'B',
                'explanation': 'The len() function returns the number of characters in the string, including the space.'
            }
        ]

        # Create questions
        for i, q_data in enumerate(questions_data, 1):
            question, created = QuizQuestion.objects.get_or_create(
                quiz=quiz,
                question_text=q_data['question_text'],
                defaults={
                    'option_a': q_data['option_a'],
                    'option_b': q_data['option_b'],
                    'option_c': q_data['option_c'],
                    'correct_answer': q_data['correct_answer'],
                    'explanation': q_data['explanation'],
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f'Created question {i}: {question.question_text[:50]}...')
            else:
                self.stdout.write(f'Question {i} already exists')

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample quiz data!')
        )