# Generated manually to align Comentario table with model.
from django.db import migrations


def ensure_comentario_columns(apps, schema_editor):
    conn = schema_editor.connection
    cursor = conn.cursor()
    existing = {
        row[1] for row in cursor.execute("PRAGMA table_info(app1_comentario);").fetchall()
    }

    if "avatar" not in existing:
        cursor.execute(
            "ALTER TABLE app1_comentario ADD COLUMN avatar varchar(300) DEFAULT ''"
        )
    if "criado_em" not in existing:
        cursor.execute(
            "ALTER TABLE app1_comentario ADD COLUMN criado_em datetime DEFAULT CURRENT_TIMESTAMP"
        )


class Migration(migrations.Migration):

    dependencies = [
        ("app1", "0010_comentario"),
    ]

    operations = [
        migrations.RunPython(ensure_comentario_columns, migrations.RunPython.noop),
    ]
