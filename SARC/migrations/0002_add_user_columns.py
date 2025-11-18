from django.db import migrations
from django.db import connection

def add_user_columns(apps, schema_editor):
    commands = [
        "ALTER TABLE SARC_usuario ADD COLUMN last_login datetime",
        "ALTER TABLE SARC_usuario ADD COLUMN is_superuser integer DEFAULT 0",
        "ALTER TABLE SARC_usuario ADD COLUMN username varchar(150)",
        "ALTER TABLE SARC_usuario ADD COLUMN first_name varchar(150)",
        "ALTER TABLE SARC_usuario ADD COLUMN last_name varchar(150)",
        "ALTER TABLE SARC_usuario ADD COLUMN email varchar(254)",
        "ALTER TABLE SARC_usuario ADD COLUMN is_staff integer DEFAULT 0",
        "ALTER TABLE SARC_usuario ADD COLUMN is_active integer DEFAULT 1",
        "ALTER TABLE SARC_usuario ADD COLUMN date_joined datetime"
    ]
    with connection.cursor() as cursor:
        existing = [row[1] for row in cursor.execute("PRAGMA table_info('SARC_usuario')").fetchall()]
        for cmd in commands:
            # extrai nome da coluna adicionada do comando
            try:
                col = cmd.split(" ADD COLUMN ")[1].split()[0]
            except Exception:
                col = None
            if col and col not in existing:
                try:
                    cursor.execute(cmd)
                except Exception:
                    # ignora falhas (coluna pode existir, constraints podem impedir etc.)
                    pass

class Migration(migrations.Migration):

    dependencies = [
        ('SARC', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_user_columns, reverse_code=migrations.RunPython.noop),
    ]