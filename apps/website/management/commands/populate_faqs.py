from django.core.management.base import BaseCommand
from apps.website.models import FAQ


class Command(BaseCommand):
    help = 'Populate FAQ data'

    def handle(self, *args, **options):
        # Clear existing FAQs
        FAQ.objects.all().delete()
        
        # Sample FAQ data
        faqs_data = [
            {
                'question': 'Profactive platformasi nima?',
                'answer': 'Profactive - bu professional ta\'lim platformasi bo\'lib, turli sohalarda kurslar va materiallar taqdim etadi. Bizning platformamiz orqali siz yuqori sifatli ta\'lim olishingiz va professional ko\'nikmalaringizni rivojlantirishingiz mumkin.',
                'category': 'Umumiy',
                'order': 1,
                'is_active': True
            },
            {
                'question': 'Kurslarga qanday ro\'yxatdan o\'tish mumkin?',
                'answer': 'Kurslarga ro\'yxatdan o\'tish uchun avval platformada ro\'yxatdan o\'ting, so\'ngra kerakli kursni tanlang va "Ro\'yxatdan o\'tish" tugmasini bosing. To\'lov amalga oshirilgandan so\'ng siz kursga kirish huquqiga ega bo\'lasiz.',
                'category': 'Ro\'yxatdan o\'tish',
                'order': 2,
                'is_active': True
            },
            {
                'question': 'To\'lov qanday amalga oshiriladi?',
                'answer': 'Biz turli to\'lov usullarini qo\'llab-quvvatlaymiz: bank kartasi, elektron to\'lov tizimlari va boshqa xavfsiz usullar. Barcha to\'lovlar xavfsiz va shifrlangan.',
                'category': 'To\'lov',
                'order': 3,
                'is_active': True
            },
            {
                'question': 'Kurs materiallariga qanday kirish mumkin?',
                'answer': 'Kurs materiallariga kirish uchun "Mening kurslarim" bo\'limiga o\'ting va kerakli kursni tanlang. U yerda barcha video darslar, matnli materiallar va vazifalar mavjud.',
                'category': 'Kurslar',
                'order': 4,
                'is_active': True
            },
            {
                'question': 'Kursni tugatgandan keyin sertifikat olish mumkinmi?',
                'answer': 'Ha, kursni muvaffaqiyatli tugatgan barcha talabalar sertifikat olish huquqiga ega. Sertifikat elektron formatda beriladi va uni LinkedIn va boshqa professional platformalarda ko\'rsatishingiz mumkin.',
                'category': 'Sertifikat',
                'order': 5,
                'is_active': True
            },
            {
                'question': 'Texnik yordam qanday olish mumkin?',
                'answer': 'Texnik yordam uchun biz bilan bog\'laning: email orqali support@profactive.uz yoki telefon orqali +998 90 123 45 67. Biz 24/7 sizga yordam beramiz.',
                'category': 'Yordam',
                'order': 6,
                'is_active': True
            },
            {
                'question': 'Kursni qayta ko\'rish mumkinmi?',
                'answer': 'Ha, kursni xohlagancha qayta ko\'rishingiz mumkin. Kursni sotib olganingizdan keyin sizga cheksiz kirish huquqi beriladi.',
                'category': 'Kurslar',
                'order': 7,
                'is_active': True
            },
            {
                'question': 'Mobil qurilmada ishlatish mumkinmi?',
                'answer': 'Ha, bizning platforma barcha qurilmalarda ishlaydi: kompyuter, planshet va mobil telefon. Responsive dizayn tufayli har qanday ekran o\'lchamida qulay foydalanish mumkin.',
                'category': 'Texnologiya',
                'order': 8,
                'is_active': True
            }
        ]
        
        # Create FAQ objects
        for faq_data in faqs_data:
            FAQ.objects.create(**faq_data)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(faqs_data)} FAQ entries')
        )
