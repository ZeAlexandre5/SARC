from django.db import migrations

def create_m2m_tables(apps, schema_editor):
    # cria tabela many-to-many entre usuario e group
    schema_editor.execute("""
    CREATE TABLE IF NOT EXISTS "SARC_usuario_groups" (
      "usuario_id" integer NOT NULL,
      "group_id" integer NOT NULL,
      FOREIGN KEY("usuario_id") REFERENCES "SARC_usuario"("id_usuario") DEFERRABLE INITIALLY DEFERRED,
      FOREIGN KEY("group_id") REFERENCES "auth_group"("id") DEFERRABLE INITIALLY DEFERRED,
      PRIMARY KEY("usuario_id","group_id")
    );
    """)
    # cria tabela many-to-many entre usuario e permission
    schema_editor.execute("""
    CREATE TABLE IF NOT EXISTS "SARC_usuario_user_permissions" (
      "usuario_id" integer NOT NULL,
      "permission_id" integer NOT NULL,
      FOREIGN KEY("usuario_id") REFERENCES "SARC_usuario"("id_usuario") DEFERRABLE INITIALLY DEFERRED,
      FOREIGN KEY("permission_id") REFERENCES "auth_permission"("id") DEFERRABLE INITIALLY DEFERRED,
      PRIMARY KEY("usuario_id","permission_id")
    );
    """)

def drop_m2m_tables(apps, schema_editor):
    schema_editor.execute('DROP TABLE IF EXISTS "SARC_usuario_groups";')
    schema_editor.execute('DROP TABLE IF EXISTS "SARC_usuario_user_permissions";')

class Migration(migrations.Migration):

    # Ajuste a dependência para apontar para a outra 0003 já existente
    dependencies = [
        ('SARC', '0003_alter_usuario_managers'),
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_m2m_tables, reverse_code=drop_m2m_tables),
    ]