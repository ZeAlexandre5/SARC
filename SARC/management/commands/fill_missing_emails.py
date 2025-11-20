from django.core.management.base import BaseCommand
from SARC.models import Usuario

class Command(BaseCommand):
    help = 'Preenche emails ausentes com placeholders únicos (execute após migrar campo nullable).'

    def handle(self, *args, **options):
        qs = Usuario.objects.filter(email__isnull=True)
        total = qs.count()
        updated = 0
        for u in qs:
            placeholder = f"user{u.pk}@local.invalid"
            # garante unicidade caso já exista (rápido loop)
            while Usuario.objects.filter(email=placeholder).exists():
                placeholder = f"user{u.pk}-{updated}@local.invalid"
                updated += 1
            u.email = placeholder
            u.save(update_fields=['email'])
            updated += 1
        self.stdout.write(self.style.SUCCESS(f'Preenchidos {updated} / {total} usuários.'))