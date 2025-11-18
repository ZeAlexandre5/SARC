from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import is_password_usable
from SARC.models import Usuario


class Command(BaseCommand):
    help = 'Converte senhas em texto (coluna senha) para hashes usando set_password() — execute APÓS migrar.'

    def handle(self, *args, **options):
        qs = Usuario.objects.all()
        updated = 0
        for u in qs:
            pwd = (u.password or '').strip()
            # se já é um hash ou senha vazia, pule
            if not pwd:
                # marcado como unusable para segurança
                u.set_unusable_password()
                u.save(update_fields=['password'])
                continue
            # heurística: se parecer hash (prefixos comuns), pule
            if pwd.startswith('pbkdf2_') or pwd.startswith('argon2$') or pwd.startswith('bcrypt'):
                continue
            # caso não pareça hash: set_password e salvar
            u.set_password(pwd)
            u.save(update_fields=['password'])
            updated += 1
        self.stdout.write(self.style.SUCCESS(f'Atualizadas {updated} contas (senhas convertidas para hash).'))